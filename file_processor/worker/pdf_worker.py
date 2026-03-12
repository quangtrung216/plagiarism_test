import json
from db.minio import get_client
from db.postgres import get_conn, release_conn
from db.milvus import connect, insert_vectors, _stable_int64
from services.embedding_service import embed_texts
from nlp.text_preprocess import preprocess_pdf_text
from services.pdf_extract import extract_pdf_text, extract_pdf_blocks_with_bbox
from services.document_service import mark_failed

def update_status(document_id, status, total_sentences=None, error_message=None):
    conn = get_conn()
    cur = conn.cursor()
    if status == "completed":
        cur.execute("UPDATE documents SET status = %s, total_sentences = %s WHERE document_id = %s", (status, total_sentences, document_id))
    elif status == "failed":
        cur.execute("UPDATE documents SET status=%s, error_message=%s, failed_at=NOW() WHERE document_id=%s", (status, error_message, document_id))
    else:
        cur.execute("UPDATE documents SET status = %s WHERE document_id = %s", (status, document_id))
    conn.commit()
    release_conn(conn)

def process_message(ch, method, props, body):
    data = json.loads(body)
    doc_id = data["doc_id"]
    path = data["path"]
    subject_id = data.get("subject_id", "default")
    document_type = data.get("document_type", "none")

    try:
        update_status(doc_id, "processing")
        # Download PDF from MinIO
        minio = get_client()
        obj = minio.get_object("plagiarism-files", path)
        pdf_bytes = obj.read()

        # Extract text from PDF
        # raw_text = extract_pdf_text(pdf_bytes)
        pages = extract_pdf_blocks_with_bbox(pdf_bytes)
        # sentences = preprocess_pdf_text(raw_text)
        if not pages:
            raise ValueError("No text extracted from PDF")        
        print("Pages extracted:", len(pages))
        all_sentences = []
        sentence_meta = []
        global_index = 0

        for page in pages:
            page_number = page["page"]
            for block_idx, block in enumerate(page["blocks"]):
                block_text = block["text"].strip()
                bbox = block["bbox"]
                if len(block_text) < 30:
                    continue
                sentences = preprocess_pdf_text(block_text)
                
                for sent_idx, sent in enumerate(sentences):
                    sent = sent.strip()
                    if len(sent) < 10:
                        continue
                    normalized = sent.lower()
                    word_count = len(sent.split())
                    all_sentences.append(sent)

                    sentence_meta.append({
                        "page_number": page_number,
                        "paragraph_index": block_idx,
                        "bbox": bbox,
                        "normalized_text": normalized,
                        "word_count": word_count,
                        "sentence_index": global_index
                    })
                    global_index += 1
        if not all_sentences:
            print("Total sentences collected:", len(all_sentences))
            raise ValueError("No valid sentences found")

        # Embedding 
        vectors = embed_texts(all_sentences)
        if len(vectors) != len(all_sentences):
            raise ValueError("Embedding size mismatch")
        
        # Convert numpy arrays to lists and ensure correct format
        if hasattr(vectors, 'tolist'):
            vectors_list = vectors.tolist()
        else:
            vectors_list = vectors
            
        # Ensure vectors_list is list of lists (not flat list)
        if vectors_list and isinstance(vectors_list[0], (int, float)):
            # This is a flat list, need to reshape
            dim = 768  # DEk21_hcmute_embedding has 768 dimensions
            num_vectors = len(vectors_list) // dim
            vectors_list = [vectors_list[i*dim:(i+1)*dim] for i in range(num_vectors)]
        
        connect()
        try:
            sentence_ids = [str(m["sentence_index"]) for m in sentence_meta]
            document_ids = [str(doc_id)] * len(vectors_list)
            # Generate primary key IDs
            primary_ids = [_stable_int64(f"{doc_id}:{m['sentence_index']}") for m in sentence_meta]
            
            milvus_ids = insert_vectors(
                vectors_list,                                 # List of lists, each with 1024 dims
                document_ids=document_ids,
                sentence_ids=sentence_ids,
                texts=all_sentences,
                subject_ids=[subject_id] * len(vectors_list),      # NEW: Add subject_id
                document_types=[document_type] * len(vectors_list),   # NEW: Add document_type
                ids=primary_ids,                               # NEW: Add primary key (already a list)
                partition_name=f"subject_{subject_id}",
            )

        except Exception as e:
            print(f"Error inserting vectors to Milvus: {str(e)}")
            raise
        if len(milvus_ids) != len(all_sentences):
            raise ValueError("Milvus insert returned unexpected number of ids")
        # save to Postgres
        conn = get_conn()
        cur = conn.cursor()
        for sent, meta, milvus_id in zip(all_sentences, sentence_meta, milvus_ids):
            sentence_id = f"{doc_id}:{meta['sentence_index']}"
            cur.execute("""
                INSERT INTO sentences
                (sentence_id, document_id, text, normalized_text,
                 word_count, sentences_index, milvus_id)
                VALUES (%s,%s,%s,%s,%s,%s,%s)
            """, (
                sentence_id,
                doc_id,
                sent,
                meta["normalized_text"],
                meta["word_count"],
                meta["sentence_index"],
                milvus_id
            ))
            # insert in sentence_layout
            cur.execute("""
                INSERT INTO sentence_layout
                (sentence_id, page_number,
                 paragraph_index, bbox)
                VALUES (%s,%s,%s,%s)
            """, (
                sentence_id,
                meta["page_number"],
                meta["paragraph_index"],
                json.dumps(meta["bbox"])
            ))
        conn.commit()
        release_conn(conn)
        update_status(doc_id, "completed", total_sentences=len(all_sentences))
    except Exception as e:
        print(f"Error processing document {doc_id}: {str(e)}")
        mark_failed(doc_id, str(e))
    finally:
        ch.basic_ack(delivery_tag=method.delivery_tag)
