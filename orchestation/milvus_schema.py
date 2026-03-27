from __future__ import annotations

from typing import Optional

from pymilvus import Collection, CollectionSchema, DataType, FieldSchema, MilvusException

from db import connect_milvus


def create_plagiarism_collection(
    *,
    collection_name: str = "plagiarism_docs",
    dim: int = 768,
    metric_type: str = "COSINE",
    alias: Optional[str] = None,
) -> Collection:
    """Create a Milvus collection for plagiarism detection demo.

    Schema:
      - id: INT64 (PK, auto_id=False)
      - subject_id: INT64 (scalar field, filter by subject)
      - minhash: VARCHAR (scalar field, filter by minhash)
      - content_vector: FLOAT_VECTOR (embedding, dim=768 by default)
      - metadata: JSON (optional)

    Returns:
      pymilvus.Collection instance (loaded).

    Raises:
      pymilvus.MilvusException if collection already exists.
    """
    if alias is None:
        alias = connect_milvus()

    # Define fields
    fields = [
        FieldSchema(
            name="id",
            dtype=DataType.INT64,
            is_primary=True,
            auto_id=False,
            description="Document or chunk ID",
        ),
        FieldSchema(
            name="subject_id",
            dtype=DataType.INT64,
            description="Subject ID for filtering (e.g., course or department)",
        ),
        FieldSchema(
            name="minhash",
            dtype=DataType.VARCHAR,
            max_length=64,
            description="MinHash signature for coarse filtering",
        ),
        FieldSchema(
            name="content_vector",
            dtype=DataType.FLOAT_VECTOR,
            dim=dim,
            description="Embedding vector of the document/chunk",
        ),
        FieldSchema(
            name="metadata",
            dtype=DataType.JSON,
            description="Additional metadata (optional)",
        ),
    ]

    schema = CollectionSchema(
        fields=fields,
        description=f"Plagiarism detection collection (dim={dim}, metric={metric_type})",
    )

    # Create collection
    collection = Collection(name=collection_name, schema=schema, using=alias)

    # Create index on vector field
    index_params = {
        "metric_type": metric_type,
        "index_type": "IVF_FLAT",
        "params": {"nlist": 128},
    }
    collection.create_index(field_name="content_vector", index_params=index_params)

    # Load collection into memory
    collection.load()
    return collection


def get_collection(collection_name: str = "plagiarism_docs", alias: Optional[str] = None) -> Collection:
    """Return an existing (loaded) collection."""
    if alias is None:
        alias = connect_milvus()

    collection = Collection(name=collection_name, using=alias)
    collection.load()
    return collection


def ensure_collection_and_index(
    *,
    collection_name: str = "plagiarism_docs",
    dim: int = 768,
    metric_type: str = "COSINE",
    alias: Optional[str] = None,
) -> Collection:
    """Create collection if not exists; otherwise return existing loaded collection."""
    if alias is None:
        alias = connect_milvus()

    try:
        collection = create_plagiarism_collection(
            collection_name=collection_name,
            dim=dim,
            metric_type=metric_type,
            alias=alias,
        )
        return collection
    except MilvusException as e:
        # If collection already exists, just load it
        if e.message and "already exists" in e.message.lower():
            return get_collection(collection_name=collection_name, alias=alias)
        else:
            raise
