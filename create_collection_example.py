#!/usr/bin/env python3
"""
Example script to create Milvus collection using orchestration methods
"""

from orchestation import create_plagiarism_collection, ensure_collection_and_index, get_collection

def main():
    # Method 1: Create new collection (will fail if already exists)
    try:
        collection = create_plagiarism_collection(
            collection_name="plagiarism_docs",
            dim=768,
            metric_type="COSINE"
        )
        print(f"Created new collection: {collection.name}")
    except Exception as e:
        print(f"Error creating collection: {e}")

    # Method 2: Ensure collection exists (recommended)
    collection = ensure_collection_and_index(
        collection_name="plagiarism_docs",
        dim=768,
        metric_type="COSINE"
    )
    print(f"Ensured collection exists: {collection.name}")

    # Method 3: Get existing collection
    try:
        collection = get_collection(collection_name="plagiarism_docs")
        print(f"Retrieved existing collection: {collection.name}")
    except Exception as e:
        print(f"Error getting collection: {e}")

if __name__ == "__main__":
    main()
