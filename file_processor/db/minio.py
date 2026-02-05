from minio import Minio
import os

_client = None

def get_client():
    global _client

    if _client is None:
        _client = Minio(
            os.getenv("MINIO_ENDPOINT"),
            os.getenv("MINIO_ACCESS_KEY"),
            os.getenv("MINIO_SECRET_KEY"),
            secure=False
        )

    return _client
