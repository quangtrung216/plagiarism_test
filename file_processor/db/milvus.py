from pymilvus import connections, Collection, utility
import os
import hashlib

_connected = False

def connect():
    global _connected

    if not _connected:
        alias = "default"  # Use default alias
        connections.connect(
            alias=alias,
            host=os.getenv("MILVUS_HOST", "localhost"),
            port=os.getenv("MILVUS_PORT", "19530"),  # Add default port
            # Remove db_name to use default database (working config)
        )
        _connected = True

COLLECTION = "plagiarism_sentences"


def _stable_int64(value: str) -> int:
    digest = hashlib.md5(value.encode("utf-8"), usedforsecurity=False).digest()
    return int.from_bytes(digest[:8], byteorder="big", signed=True)


def insert_vectors(vectors, document_ids=None, sentence_ids=None, texts=None, ids=None, partition_name=None, subject_ids=None, document_types=None):
    """
    Insert vectors vào Milvus với support cho các fields mới
    Schema order: id, embedding, document_id, sentence_id, text, subject_id, document_type
    """
    col = Collection(COLLECTION)
    
    # Build insert data in exact schema order
    insert_data = []
    
    # 1. id (INT64 primary key) - REQUIRED
    if ids is not None:
        insert_data.append(ids)
    else:
        raise ValueError("ids parameter is required for primary key")
    
    # 2. embedding (FloatVector) - REQUIRED
    insert_data.append(vectors)
    
    # 3. document_id (VarChar) - REQUIRED
    if document_ids is not None:
        insert_data.append(document_ids)
    else:
        raise ValueError("document_ids parameter is required")
    
    # 4. sentence_id (VarChar) - REQUIRED
    if sentence_ids is not None:
        insert_data.append(sentence_ids)
    else:
        raise ValueError("sentence_ids parameter is required")
    
    # 5. text (VarChar) - REQUIRED
    if texts is not None:
        insert_data.append(texts)
    else:
        raise ValueError("texts parameter is required")
    
    # 6. subject_id (VarChar) - OPTIONAL but recommended
    if subject_ids is not None:
        insert_data.append(subject_ids)
    else:
        # Add empty list if not provided
        insert_data.append([""] * len(vectors))
    
    # 7. document_type (VarChar) - OPTIONAL but recommended
    if document_types is not None:
        insert_data.append(document_types)
    else:
        # Add empty list if not provided
        insert_data.append([""] * len(vectors))
    
    # Insert with partition if specified
    if partition_name:
        if not col.has_partition(partition_name):
            col.create_partition(partition_name)
        res = col.insert(insert_data, partition_name=partition_name)
    else:
        res = col.insert(insert_data)
    
    col.flush()
    
    # Return primary keys if available
    return res.primary_keys if hasattr(res, 'primary_keys') else None


