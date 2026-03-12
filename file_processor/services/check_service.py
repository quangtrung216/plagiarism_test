import io
import os
import uuid
import re
import fitz
from db.minio import get_client
from db.milvus import connect
from db.postgres import get_conn, release_conn
from pymilvus import Collection
from services.embedding_service import embed_texts
from services.pdf_extract import extract_pdf_blocks_with_bbox
from services.subject_service import validate_subject_exists
from nlp.text_preprocess import preprocess_pdf_text, START_CONTENT, STOP_CONTENT


def _milvus_metric_and_dim(col: Collection):
    metric_type = "COSINE"
    dim = 768
    if col.indexes:
        metric_type = col.indexes[0].params.get("metric_type", metric_type)
    for f in col.schema.fields:
        if str(f.dtype) == "101":
            dim = int(getattr(f, "params", {}).get("dim", dim) or dim)
            break
    return metric_type, dim


def _distance_to_similarity(metric_type: str, distance: float) -> float:
    metric_type = (metric_type or "").upper()
    if metric_type == "COSINE":
        # Milvus versions differ on what is returned in hit.distance for COSINE.
        # Some return distance (1 - cosine_similarity), others return cosine_similarity directly.
        # Be robust by selecting the value that most resembles a similarity score.
        d = float(distance)
        sim_candidates = [d, 1.0 - d]
        sim = max(sim_candidates)
        return max(-1.0, min(1.0, sim))
    if metric_type == "IP":
        return float(distance)
    if metric_type == "L2":
        return 1.0 / (1.0 + float(distance))
    return float(distance)


def _get_document_filename(doc_id: str):
    conn = get_conn()
    try:
        cur = conn.cursor()
        try:
            cur.execute("SELECT filename FROM documents WHERE document_id = %s", (doc_id,))
            row = cur.fetchone()
            return row[0] if row else None
        finally:
            cur.close()
    finally:
        release_conn(conn)


def _highlight_pdf(pdf_bytes: bytes, highlights: list[dict]) -> bytes:
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    for h in highlights:
        page_index = int(h["page_number"]) - 1
        if page_index < 0 or page_index >= len(doc):
            continue
        page = doc[page_index]
        bbox = h.get("bbox")
        if not bbox or len(bbox) != 4:
            continue
        rect = fitz.Rect(bbox)
        annot = page.add_highlight_annot(rect)
        annot.update()
    out = doc.tobytes()
    doc.close()
    return out


def _find_content_page_range(pages: list[dict]) -> tuple[int, int]:
    start_page = 1
    stop_page = pages[-1]["page"] if pages else 0

    found_start = False
    for page in pages:
        page_no = page.get("page")
        for block in page.get("blocks", []):
            text = (block.get("text") or "").strip().upper()
            if not text:
                continue
            if not found_start:
                for pattern in START_CONTENT:
                    if re.search(pattern, text):
                        start_page = page_no
                        found_start = True
                        break
            if any(keyword in text for keyword in STOP_CONTENT):
                stop_page = page_no
                return start_page, stop_page

    return start_page, stop_page


async def handle_check(file, subject_id: str = "", document_type: str = ""):
    content = await file.read()
    
    # Validate subject if provided
    if subject_id and not validate_subject_exists(subject_id):
        return {"error": f"Subject '{subject_id}' does not exist"}

    pages = extract_pdf_blocks_with_bbox(content)
    if not pages:
        return {"error": "No text extracted from PDF"}

    start_page, stop_page = _find_content_page_range(pages)

    all_sentences: list[str] = []
    sentence_meta: list[dict] = []
    global_index = 0

    for page in pages:
        page_number = page["page"]
        if page_number < start_page or page_number > stop_page:
            continue
        for block_idx, block in enumerate(page["blocks"]):
            block_text = block["text"].strip()
            bbox = block["bbox"]
            if len(block_text) < 30:
                continue
            sentences = preprocess_pdf_text(block_text, min_words=5, use_zone=False)
            for sent in sentences:
                sent = sent.strip()
                if len(sent) < 10:
                    continue
                all_sentences.append(sent)
                sentence_meta.append(
                    {
                        "page_number": page_number,
                        "paragraph_index": block_idx,
                        "bbox": bbox,
                        "sentence_index": global_index,
                    }
                )
                global_index += 1

    if not all_sentences:
        return {"error": "No valid sentences found"}

    vectors = embed_texts(all_sentences)
    connect()

    # Get candidate document_ids from Postgres based on subject_id and document_type filtering
    candidate_doc_ids = None
    if subject_id or document_type:
        conn = get_conn()
        try:
            cur = conn.cursor()
            try:
                query = "SELECT document_id FROM documents WHERE 1=1"
                params = []
                if subject_id:
                    query += " AND subject_id = %s"
                    params.append(subject_id)
                if document_type:
                    query += " AND document_type = %s"
                    params.append(document_type)
                cur.execute(query, params)
                rows = cur.fetchall()
                candidate_doc_ids = [row[0] for row in rows]
            finally:
                cur.close()
        finally:
            release_conn(conn)

    collection_name = os.getenv("MILVUS_COLLECTION", "plagiarism_sentences")
    alias = os.getenv("MILVUS_ALIAS", "plagiarism_db")
    col = Collection(collection_name, using=alias)
    
    # Use partition based on subject_id if provided
    partition_name = None
    if subject_id:
        partition_name = f"subject_{subject_id}"
        print(f"DEBUG: Using partition: {partition_name}")
    
    col.load(partition_names=[partition_name] if partition_name else None)
    print(f"DEBUG: Loaded collection with partition: {partition_name or 'all'}")

    metric_type, _ = _milvus_metric_and_dim(col)
    top_k = int(os.getenv("PLAGIARISM_TOPK", "3"))
    sentence_threshold = float(os.getenv("PLAGIARISM_SENTENCE_SIM_THRESHOLD", "0.6"))

    search_params = {"metric_type": metric_type, "params": {"nprobe": 10}}

    # Add document_id filter if we have candidate documents
    expr = None
    if candidate_doc_ids and len(candidate_doc_ids) > 0:
        # Create expression for filtering by document_id list
        doc_id_list = ", ".join([f'"{doc_id}"' for doc_id in candidate_doc_ids])
        expr = f"document_id in [{doc_id_list}]"
        print(f"DEBUG: Filtering by {len(candidate_doc_ids)} candidate documents")
        print(f"DEBUG: Expression: {expr}")
    elif subject_id or document_type:
        print(f"DEBUG: No candidate documents found for subject_id={subject_id}, document_type={document_type}")
        return {"error": "No reference documents found for the specified subject and document type"}

    results = col.search(
        data=vectors,
        anns_field="embedding",
        param=search_params,
        limit=top_k,
        output_fields=["document_id", "sentence_id", "text"],
        expr=expr,
    )

    matched: list[dict] = []
    per_source: dict[str, dict] = {}

    debug = os.getenv("PLAGIARISM_DEBUG") == "1"

    for idx, hits in enumerate(results):
        if not hits:
            continue
        best = hits[0]
        sim = _distance_to_similarity(metric_type, best.distance)
        if debug and idx < 3:
            print(
                "DEBUG check hit",
                {"idx": idx, "metric": metric_type, "raw_distance": float(best.distance), "similarity": sim},
            )
        if sim < sentence_threshold:
            continue

        entity = best.entity
        src_doc_id = entity.get("document_id")
        src_sentence_id = entity.get("sentence_id")
        src_text = entity.get("text")

        if src_doc_id not in per_source:
            per_source[src_doc_id] = {"count": 0}
        per_source[src_doc_id]["count"] += 1

        matched.append(
            {
                "query_sentence_index": sentence_meta[idx]["sentence_index"],
                "page_number": sentence_meta[idx]["page_number"],
                "bbox": sentence_meta[idx]["bbox"],
                "similarity": sim,
                "raw_distance": float(best.distance),
                "metric_type": metric_type,
                "source_document_id": src_doc_id,
                "source_sentence_id": src_sentence_id,
                "source_text": src_text,
            }
        )

    total = len(all_sentences)
    matched_count = len(matched)
    overall_ratio = matched_count / total if total else 0.0

    plagiarism_threshold = float(os.getenv("PLAGIARISM_DOCUMENT_MATCH_THRESHOLD", "0.2"))
    is_plagiarism = overall_ratio >= plagiarism_threshold

    sources = []
    for doc_id, info in per_source.items():
        sources.append(
            {
                "document_id": doc_id,
                "filename": _get_document_filename(doc_id),
                "matched_sentences": info["count"],
                "matched_ratio": info["count"] / total if total else 0.0,
            }
        )
    sources.sort(key=lambda x: x["matched_sentences"], reverse=True)
    best_source_document_id = sources[0]["document_id"] if sources else None

    result_pdf_bytes = _highlight_pdf(content, matched)

    minio = get_client()
    result_bucket = os.getenv("MINIO_RESULT_BUCKET", "result")
    result_id = str(uuid.uuid4())
    result_path = f"result/{result_id}.pdf"
    minio.put_object(
        result_bucket,
        result_path,
        io.BytesIO(result_pdf_bytes),
        length=len(result_pdf_bytes),
        content_type="application/pdf",
    )

    return {
        "total_sentences": total,
        "matched_sentences": matched_count,
        "matched_ratio": overall_ratio,
        "is_plagiarism": is_plagiarism,
        "threshold": plagiarism_threshold,
        "sentence_similarity_threshold": sentence_threshold,
        "best_source_document_id": best_source_document_id,
        "top_sources": sources[:5],
        "matches": matched,
        "result_pdf": {
            "bucket": result_bucket,
            "path": result_path,
        },
    }
