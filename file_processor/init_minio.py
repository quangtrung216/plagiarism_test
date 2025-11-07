"""
Script to initialize MinIO bucket for file processing
"""

import os
from minio import Minio
from minio.error import S3Error


def init_minio_bucket():
    # MinIO configuration from environment variables
    MINIO_ENDPOINT = os.getenv("MINIO_ENDPOINT", "localhost:9000")
    MINIO_ACCESS_KEY = os.getenv("MINIO_ACCESS_KEY", "minioadmin")
    MINIO_SECRET_KEY = os.getenv("MINIO_SECRET_KEY", "minioadmin")
    MINIO_BUCKET_NAME = os.getenv("MINIO_BUCKET_NAME", "plagiarism-files")
    MINIO_SECURE = os.getenv("MINIO_SECURE", "False").lower() == "true"

    # Initialize MinIO client
    minio_client = Minio(
        MINIO_ENDPOINT,
        access_key=MINIO_ACCESS_KEY,
        secret_key=MINIO_SECRET_KEY,
        secure=MINIO_SECURE,
    )

    try:
        # Create bucket if it doesn't exist
        if not minio_client.bucket_exists(MINIO_BUCKET_NAME):
            minio_client.make_bucket(MINIO_BUCKET_NAME)
            print(f"Bucket '{MINIO_BUCKET_NAME}' created successfully")
        else:
            print(f"Bucket '{MINIO_BUCKET_NAME}' already exists")

    except S3Error as e:
        print(f"MinIO error: {e}")
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    init_minio_bucket()
