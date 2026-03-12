import hashlib 
import uuid 
from db.postgres import get_conn, release_conn
from db.minio import get_client
from rabbit_queue.publisher import publish_task
from services.subject_service import validate_subject_exists
import io

async def handle_upload(file, subject_id: str, document_type: str = "none"):
    content = await file.read()
    file_hash = hashlib.sha256(content).hexdigest()
    
    # Validate subject exists
    if not validate_subject_exists(subject_id):
        raise ValueError(f"Subject '{subject_id}' does not exist")
    
    conn = get_conn()
    try:
        cur = conn.cursor()
        try:
            cur.execute("SELECT document_id FROM documents WHERE file_hash = %s", (file_hash,))
            row = cur.fetchone()
            if row:
                return row[0]
        finally:
            cur.close()
    finally:
        release_conn(conn)
    
    #Upload to MinIO
    file_id = str(uuid.uuid4())
    path = f"raw/{file_id}.pdf"
    minio = get_client()
    data = io.BytesIO(content)
    minio.put_object(
        "plagiarism-files",
        path,
        data,
        len(content),
        content_type="application/pdf"
    )

    #Insert to metadata DB
    conn = get_conn()
    try:
        cur = conn.cursor()
        try:
            cur.execute("""
                INSERT INTO documents
                (document_id, filename, minio_path, file_hash, status, subject_id, document_type)
                VALUES (%s,%s,%s,%s,'pending',%s,%s)
                RETURNING document_id
            """, (
                file_id,
                file.filename,
                path,
                file_hash,
                subject_id,
                document_type
            ))
            doc_id = cur.fetchone()[0]
            conn.commit()
        finally:
            cur.close()
    finally:
        release_conn(conn)
    publish_task({
        "doc_id": doc_id,
        "path": path,
        "subject_id": subject_id,
        "document_type": document_type,
    })

    return doc_id

