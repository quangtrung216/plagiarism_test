from db.postgres import get_conn, release_conn


def mark_failed(doc_id: int, reason: str = None):

    conn = get_conn()
    cur = conn.cursor()

    cur.execute("""
        UPDATE documents
        SET status = 'failed',
            error_message = %s
        WHERE id = %s
    """, (
        reason,
        doc_id
    ))

    conn.commit()

    release_conn(conn)

    print(f"Document {doc_id} marked as failed")
