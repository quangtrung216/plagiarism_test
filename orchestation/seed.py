from __future__ import annotations

from typing import List, Sequence

from pymilvus import Collection

from .milvus_schema import create_plagiarism_collection, get_collection


def insert_demo_docs(
    collection: Collection,
    docs: Sequence[dict],
    batch_size: int = 1000,
) -> List[int]:
    """Insert a batch of demo docs into the plagiarism collection.

    Expected keys in each doc dict:
      - id (int)
      - subject_id (int)
      - minhash (str, <=64 chars)
      - content_vector (list[float], length must match collection dim)
      - metadata (dict, optional)

    Returns:
      List of inserted IDs (same order as input).
    """
    # Validate required keys
    required_keys = {"id", "subject_id", "minhash", "content_vector"}
    for d in docs:
        missing = required_keys - d.keys()
        if missing:
            raise ValueError(f"Missing keys {missing} in doc: {d}")

    # Insert in batches
    inserted_ids: List[int] = []
    for i in range(0, len(docs), batch_size):
        batch = docs[i : i + batch_size]
        ids = [int(d["id"]) for d in batch]
        subject_ids = [int(d["subject_id"]) for d in batch]
        minhashes = [str(d["minhash"]) for d in batch]
        vectors = [list(d["content_vector"]) for d in batch]
        metadatas = [d.get("metadata", {}) for d in batch]

        mr = collection.insert(
            data=[
                ids,
                subject_ids,
                minhashes,
                vectors,
                metadatas,
            ]
        )
        inserted_ids.extend(mr.primary_keys)

    # Flush to make data searchable
    collection.flush()
    return inserted_ids


def demo_search(
    collection: Collection,
    query_vector: Sequence[float],
    *,
    subject_id: Optional[int] = None,
    minhash: Optional[str] = None,
    top_k: int = 10,
    offset: int = 0,
) -> List[dict]:
    """Search with optional scalar filters (subject_id, minhash).

    Returns a list of dicts with keys: id, subject_id, minhash, content_vector, metadata, distance.
    """
    expr_parts = []
    if subject_id is not None:
        expr_parts.append(f"subject_id == {subject_id}")
    if minhash is not None:
        expr_parts.append(f'minhash == "{minhash}"')
    expr = " and ".join(expr_parts) if expr_parts else None

    results = collection.search(
        data=[list(query_vector)],
        anns_field="content_vector",
        param={"metric_type": "COSINE", "params": {"nprobe": 10}},
        limit=top_k,
        offset=offset,
        expr=expr,
        output_fields=["id", "subject_id", "minhash", "metadata"],
    )[0]

    formatted = []
    for hit in results:
        formatted.append(
            {
                "id": hit.entity.get("id"),
                "subject_id": hit.entity.get("subject_id"),
                "minhash": hit.entity.get("minhash"),
                "metadata": hit.entity.get("metadata"),
                "distance": hit.distance,
            }
        )
    return formatted
