import hashlib 
import uuid 
from db.postgres import get_conn, release_conn
from db.minio import get_client
from rabbit_queue.publisher import publish_task
import io

async def handle_upload(file):
    content = await file.read()
    file_hash = hashlib.sha256(content).hexdigest()
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT id FROM documents WHERE file_hash = %s", (file_hash,))
    row = cur.fetchone()
    if row:
        return row[0]
    
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
    cur.execute("""
        INSERT INTO documents
        (file_name, file_path, file_hash, status)
        VALUES (%s,%s,%s,'pending')
        RETURNING id
    """, (
        file.filename,
        path,
        file_hash
    ))
    doc_id = cur.fetchone()[0]
    conn.commit()
    release_conn(conn)
    publish_task({
        "doc_id": doc_id,
        "path": path
    })

    return doc_id

