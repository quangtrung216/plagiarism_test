"""
MinIO client utility for file storage
"""

import os
from typing import Optional
from minio import Minio
from minio.error import S3Error
from app.core.config import settings

# Initialize MinIO client
minio_client = Minio(
    settings.MINIO_ENDPOINT,
    access_key=settings.MINIO_ACCESS_KEY,
    secret_key=settings.MINIO_SECRET_KEY,
    secure=settings.MINIO_SECURE,
)


def upload_file_to_minio(
    file_data: bytes, file_name: str, bucket_name: Optional[str] = None
) -> str:
    """
    Upload a file to MinIO and return the object name

    Args:
        file_data: File content as bytes
        file_name: Original file name
        bucket_name: Bucket name (uses default if not provided)

    Returns:
        str: Object name in MinIO
    """
    try:
        if bucket_name is None:
            bucket_name = settings.MINIO_BUCKET_NAME

        # Ensure bucket exists
        if not minio_client.bucket_exists(bucket_name):
            minio_client.make_bucket(bucket_name)

        # Generate unique object name
        import uuid

        file_extension = os.path.splitext(file_name)[1] if file_name else ""
        object_name = f"{uuid.uuid4()}{file_extension}"

        # Upload file
        minio_client.put_object(
            bucket_name,
            object_name,
            data=bytes(file_data),
            length=len(file_data),
            content_type="application/octet-stream",
        )

        return object_name
    except S3Error as e:
        print(f"MinIO error: {e}")
        raise Exception(f"Failed to upload file to MinIO: {e}")
    except Exception as e:
        print(f"Error: {e}")
        raise Exception(f"Failed to upload file: {e}")


def get_file_from_minio(object_name: str, bucket_name: Optional[str] = None) -> bytes:
    """
    Retrieve a file from MinIO

    Args:
        object_name: Object name in MinIO
        bucket_name: Bucket name (uses default if not provided)

    Returns:
        bytes: File content
    """
    try:
        if bucket_name is None:
            bucket_name = settings.MINIO_BUCKET_NAME

        # Get file from MinIO
        response = minio_client.get_object(bucket_name, object_name)
        file_data = response.data
        response.close()
        response.release_conn()

        return file_data
    except S3Error as e:
        print(f"MinIO error: {e}")
        raise Exception(f"Failed to retrieve file from MinIO: {e}")
    except Exception as e:
        print(f"Error: {e}")
        raise Exception(f"Failed to retrieve file: {e}")


def delete_file_from_minio(object_name: str, bucket_name: Optional[str] = None) -> bool:
    """
    Delete a file from MinIO

    Args:
        object_name: Object name in MinIO
        bucket_name: Bucket name (uses default if not provided)

    Returns:
        bool: True if successful
    """
    try:
        if bucket_name is None:
            bucket_name = settings.MINIO_BUCKET_NAME

        # Delete file from MinIO
        minio_client.remove_object(bucket_name, object_name)

        return True
    except S3Error as e:
        print(f"MinIO error: {e}")
        raise Exception(f"Failed to delete file from MinIO: {e}")
    except Exception as e:
        print(f"Error: {e}")
        raise Exception(f"Failed to delete file: {e}")
