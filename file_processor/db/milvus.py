from pymilvus import connections, Collection, utility
import os

_connected = False

def connect():
    global _connected

    if not _connected:
        connections.connect(
            host=os.getenv("MILVUS_HOST"),
            port=os.getenv("MILVUS_PORT"),
            db_name=os.getenv("MILVUS_DB")
        )
        _connected = True

COLLECTION = "reference_vectors"


def insert_vectors(vectors):

    col = Collection(COLLECTION)

    res = col.insert([vectors])

    col.flush()

    return res.primary_keys


