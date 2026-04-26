from db.postgres import get_conn, release_conn # file liên quan tới môn học - ko cần quan tâm

def get_all_subjects():
    """Get all subjects from database"""
    conn = get_conn()
    try:
        cur = conn.cursor()
        try:
            cur.execute("""
                SELECT subject_id, subject_name, description, created_at, updated_at 
                FROM subjects 
                ORDER BY subject_name
            """)
            rows = cur.fetchall()
            return [
                {
                    "subject_id": row[0],
                    "subject_name": row[1], 
                    "description": row[2],
                    "created_at": row[3],
                    "updated_at": row[4]
                }
                for row in rows
            ]
        finally:
            cur.close()
    finally:
        release_conn(conn)

def get_subject_by_id(subject_id: str):
    """Get a specific subject by ID"""
    conn = get_conn()
    try:
        cur = conn.cursor()
        try:
            cur.execute("""
                SELECT subject_id, subject_name, description, created_at, updated_at 
                FROM subjects 
                WHERE subject_id = %s
            """, (subject_id,))
            row = cur.fetchone()
            if row:
                return {
                    "subject_id": row[0],
                    "subject_name": row[1],
                    "description": row[2], 
                    "created_at": row[3],
                    "updated_at": row[4]
                }
            return None
        finally:
            cur.close()
    finally:
        release_conn(conn)

def create_subject(subject_id: str, subject_name: str, description: str = None):
    """Create a new subject"""
    conn = get_conn()
    try:
        cur = conn.cursor()
        try:
            cur.execute("""
                INSERT INTO subjects (subject_id, subject_name, description)
                VALUES (%s, %s, %s)
                RETURNING subject_id, subject_name, description, created_at, updated_at
            """, (subject_id, subject_name, description))
            row = cur.fetchone()
            conn.commit()
            return {
                "subject_id": row[0],
                "subject_name": row[1],
                "description": row[2],
                "created_at": row[3],
                "updated_at": row[4]
            }
        finally:
            cur.close()
    finally:
        release_conn(conn)

def validate_subject_exists(subject_id: str) -> bool:
    """Check if a subject exists"""
    if not subject_id:
        return False
    return get_subject_by_id(subject_id) is not None
