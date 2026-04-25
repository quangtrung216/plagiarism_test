import hashlib
import io
import os
import tempfile
import uuid
from pathlib import Path

from db.postgres import get_conn, release_conn
from db.minio import get_client
from db.milvus import connect as milvus_connect, insert_vectors
from model.doc import DocUpResponse, UploadBatchResponse
from services.embedding_service import embed_texts
from services.file_process_service import FileProcessService
from services.minhash import compute_minhash
from services.subject_service import validate_subject_exists
from nlp.text_preprocess import extract_plagiarism_zone, normalize_full_text, preprocess_pdf_text

def _detect_file_type(filename: str) -> str:
    ext = Path(filename).suffix.lower()
    if ext == ".pdf":
        return "pdf"
    if ext == ".docx":
        return "docx"
    return ""


def _minio_content_type(file_type: str) -> str:
    if file_type == "pdf":
        return "application/pdf"
    if file_type == "docx":
        return "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    return "application/octet-stream"


async def _handle_single_upload_and_embed(
    file,
    subject_id: str,
    document_type: str,
    language: str,
    min_words: int,
    max_words: int,
    use_zone: bool,
) -> DocUpResponse:
    if not file.filename:
        raise ValueError("Missing uploaded filename")

    file_type = _detect_file_type(file.filename)
    if file_type not in {"pdf", "docx"}:
        raise ValueError(f"Unsupported file type: {Path(file.filename).suffix.lower()}")

    content = await file.read()
    file_hash = hashlib.sha256(content).hexdigest()

    if not validate_subject_exists(subject_id):
        raise ValueError(f"Subject '{subject_id}' does not exist")

    conn = get_conn()
    try:
        cur = conn.cursor()
        try:
            cur.execute("SELECT document_id FROM documents WHERE file_hash = %s", (file_hash,))
            row = cur.fetchone()
            if row:
                file_id = row[0]
            else:
                file_id = None
        finally:
            cur.close()
    finally:
        release_conn(conn)

    if file_id is None:
        file_id = str(uuid.uuid4())

    bucket = os.getenv("MINIO_RAW_BUCKET", "plagiarism-files")
    path = f"raw/{file_id}.{file_type}"
    minio = get_client()
    minio.put_object(
        bucket,
        path,
        io.BytesIO(content),
        len(content),
        content_type=_minio_content_type(file_type),
    )

    conn = get_conn()
    try:
        cur = conn.cursor()
        try:
            cur.execute(
                """
                INSERT INTO documents
                (document_id, filename, minio_path, file_hash, status, subject_id, document_type)
                VALUES (%s,%s,%s,%s,'processed',%s,%s)
                ON CONFLICT (document_id) DO UPDATE SET
                    filename = EXCLUDED.filename,
                    minio_path = EXCLUDED.minio_path,
                    file_hash = EXCLUDED.file_hash,
                    status = EXCLUDED.status,
                    subject_id = EXCLUDED.subject_id,
                    document_type = EXCLUDED.document_type
                RETURNING document_id
                """,
                (
                    file_id,
                    file.filename,
                    path,
                    file_hash,
                    subject_id,
                    document_type,
                ),
            )
            doc_id = cur.fetchone()[0]
            conn.commit()
        finally:
            cur.close()
    finally:
        release_conn(conn)

    tmp_path = None
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=f".{file_type}") as tmp:
            tmp.write(content)
            tmp_path = tmp.name

        extracted = FileProcessService.extract_text_from_file(tmp_path, file_type=file_type)
        if not extracted.get("success"):
            raise ValueError(extracted.get("error") or "Failed to extract text")

        extracted_text = extracted.get("text") or ""
        normalized_text = normalize_full_text(extracted_text)
        zone_text = extract_plagiarism_zone(normalized_text) if use_zone else normalized_text
        minhash_source_text = zone_text.strip() or normalized_text

        if minhash_source_text.strip():
            doc_minhash = compute_minhash(minhash_source_text)
            conn = get_conn()
            try:
                cur = conn.cursor()
                try:
                    cur.execute(
                        "UPDATE documents SET minhash = %s WHERE document_id = %s",
                        (doc_minhash, doc_id),
                    )
                    conn.commit()
                finally:
                    cur.close()
            finally:
                release_conn(conn)

        sentences = preprocess_pdf_text(
            raw_text=zone_text,
            language=language,
            min_words=min_words,
            max_words=max_words,
            use_zone=False,
        )
        if sentences:
            vectors = embed_texts(sentences)

            ids = []
            sentence_ids = []
            document_ids = []
            texts = []
            subject_ids = []
            document_types = []

            for i, s in enumerate(sentences):
                stable_id_source = f"{doc_id}:{i}:{s}"
                digest = hashlib.md5(stable_id_source.encode("utf-8"), usedforsecurity=False).digest()
                pk = int.from_bytes(digest[:8], byteorder="big", signed=True)
                ids.append(pk)
                sentence_ids.append(f"{doc_id}_{i}")
                document_ids.append(doc_id)
                texts.append(s)
                subject_ids.append(subject_id)
                document_types.append(document_type or "")

            milvus_connect()
            partition_name = f"subject_{subject_id}" if subject_id else None
            insert_vectors(
                vectors=vectors,
                document_ids=document_ids,
                sentence_ids=sentence_ids,
                texts=texts,
                ids=ids,
                partition_name=partition_name,
                subject_ids=subject_ids,
                document_types=document_types,
            )

    finally:
        try:
            if tmp_path:
                Path(tmp_path).unlink(missing_ok=True)
        except TypeError:
            if tmp_path and Path(tmp_path).exists():
                Path(tmp_path).unlink()
        except Exception:
            pass

    return DocUpResponse(
        document_id=doc_id,
        file_name=file.filename,
        subject_id=subject_id,
        file_path=path,
    )


async def handle_upload(file, subject_id: str, document_type: str = "none"):
    doc = await _handle_single_upload_and_embed(
        file=file,
        subject_id=subject_id,
        document_type=document_type,
        language="vi",
        min_words=8,
        max_words=200,
        use_zone=False,
    )
    return doc.document_id


async def handle_upload_doc(file, subject_id: str, document_type: str = "none") -> DocUpResponse:
    return await _handle_single_upload_and_embed(
        file=file,
        subject_id=subject_id,
        document_type=document_type,
        language="vi",
        min_words=8,
        max_words=200,
        use_zone=False,
    )


async def handle_upload_batch(
    files,
    subject_id: str,
    document_type: str = "none",
    language: str = "vi",
    min_words: int = 8,
    max_words: int = 200,
    use_zone: bool = False,
) -> UploadBatchResponse:
    documents: list[DocUpResponse] = []
    errors: list[dict] = []

    for f in files:
        try:
            doc = await _handle_single_upload_and_embed(
                file=f,
                subject_id=subject_id,
                document_type=document_type,
                language=language,
                min_words=min_words,
                max_words=max_words,
                use_zone=use_zone,
            )
            documents.append(doc)
        except Exception as e:
            errors.append({"file_name": getattr(f, "filename", None), "error": str(e)})

    total = len(files)
    succeeded = len(documents)
    failed = len(errors)
    return UploadBatchResponse(
        total=total,
        succeeded=succeeded,
        failed=failed,
        documents=documents,
        errors=errors,
    )

