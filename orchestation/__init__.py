from .milvus_schema import (
    create_plagiarism_collection,
    get_collection,
    ensure_collection_and_index,
)

__all__ = [
    "create_plagiarism_collection",
    "get_collection",
    "ensure_collection_and_index",
]
