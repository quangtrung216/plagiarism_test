import json
from db.minio import get_client
from db.postgres import get_conn, release_conn
from db.milvus import connect, insert_vectors
from services.embedding_service import embed_texts
from nlp.text_preprocess import preprocess_pdf_text
from services.pdf_extract import extract_pdf_text, extract_pdf_blocks_with_bbox
from services.document_service import mark_failed

def process_message(ch, method, props, body):
    data = json.loads(body)
    doc_id = data["doc_id"]
    path = data["path"]

    1# Download PDF from MinIO
    minio = get_client()
    obj = minio.get_object("plagiarism-files", path)
    print("DEBUG MinIO path:", path)
    pdf_bytes = obj.read()

    # Extract text from PDF
    # raw_text = extract_pdf_text(pdf_bytes)
    pages = extract_pdf_blocks_with_bbox(pdf_bytes)
    # sentences = preprocess_pdf_text(raw_text)

    if not pages:
        mark_failed(doc_id)
        ch.basic_ack(delivery_tag=method.delivery_tag)
        return
    all_sentences = []
    sentence_meta = []

    for page in pages:
        page_number = page["page"]
        for block_idx, block in enumerate(page["blocks"]):
            block_text = block["text"]
            bbox = block["bbox"]
            sentences = preprocess_pdf_text(block_text)
            if not sentences:
                continue
            
            for order, sent in enumerate(sentences):

                all_sentences.append(sent)

                sentence_meta.append({
                    "page_number": page_number,
                    "paragraph_index": block_idx,
                    "sentence_order": order,
                    "bbox": bbox
                })
    if not all_sentences:
        mark_failed(doc_id)
        ch.basic_ack(delivery_tag=method.delivery_tag)
        return

    # Embedding 
    vectors = embed_texts(all_sentences)
    connect()
    milvus_ids = insert_vectors(vectors)
    # save to Postgres
    conn = get_conn()
    cur = conn.cursor()
    for s, meta, mid in zip(all_sentences, sentence_meta, milvus_ids):
         cur.execute("""
            INSERT INTO sentences
            (document_id, page_number, paragraph_index, sentence_order, sentence_text, bbox, milvus_id)
            VALUES (%s,%s,%s,%s,%s,%s,%s)
        """, (
            doc_id,
            meta["page_number"],
            meta["paragraph_index"],
            meta["sentence_order"],
            s,
            json.dumps(meta["bbox"]),
            mid
        ))
    # update document status
    cur.execute("""
        UPDATE documents
        SET status='done'
        WHERE id=%s
    """, (doc_id,))

    conn.commit()
    release_conn(conn)

    ch.basic_ack(delivery_tag=method.delivery_tag)
