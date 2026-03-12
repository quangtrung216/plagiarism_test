from db.postgres import get_conn, release_conn


def mark_failed(doc_id: str, reason: str = None):

    conn = get_conn()
    try: 
        cur = conn.cursor()

        cur.execute("""
            UPDATE documents
            SET status = 'failed',
                error_message = %s,
                failed_at = NOW()
            WHERE document_id = %s
                AND status = 'processing'
        """, (
            reason,
            doc_id
        ))
        if cur.rowcount == 0:
            print(f"Document {doc_id} is not in processing state, cannot mark as failed")
        conn.commit()
        cur.close()
        print(f"Document {doc_id} marked as failed")
    except Exception as e:
        conn.rollback()
        print(f"Failed to update document {doc_id}: {str(e)}")
        raise
    finally:
        release_conn(conn)