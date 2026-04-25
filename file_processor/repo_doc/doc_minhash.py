import psycopg2.extensions
from services.minhash import jaccard_similarity

async def find_candidates_by_minhash(
    conn: psycopg2.extensions.connection,
    minhash: list[int],
    subject_id: str,
    threshold: float = 0.5,
) -> list[dict]:
    """
    Lọc thô: lấy các tài liệu tham chiếu cùng môn học,
    tính Jaccard similarity qua MinHash,
    trả về các tài liệu có similarity >= threshold.
    """
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT document_id, filename, subject_id, minhash
        FROM documents
        WHERE subject_id = %s
          AND minhash IS NOT NULL
        """,
        (subject_id,),
    )
    rows = cursor.fetchall()

    candidates = []
    for row in rows:
        document_id, file_name, subject_id, minhash_data = row
        sim = jaccard_similarity(minhash, list(minhash_data))
        if sim >= threshold:
            candidates.append({
                "document_id": str(document_id),
                "file_name":   file_name,
                "subject_id":  subject_id,
                "jaccard_similarity": round(sim, 4),
            })

    return sorted(candidates, key=lambda x: x["jaccard_similarity"], reverse=True)