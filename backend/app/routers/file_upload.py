"""
Example of how to integrate file processing with RabbitMQ in an API endpoint
This would be added to a router in the backend application
"""

from fastapi import APIRouter, UploadFile, File, HTTPException
from typing import Dict, Any
import uuid
from app.utils.rabbitmq_publisher import send_file_for_processing
from app.utils.minio_client import upload_file_to_minio

router = APIRouter()


@router.post("/upload-file/")
async def upload_file(file: UploadFile = File(...)):
    """
    Upload a file to MinIO and send its reference for processing via RabbitMQ
    """
    try:
        # Read file content
        content = await file.read()

        # Upload file to MinIO
        file_name = file.filename if file.filename else "unnamed_file"
        object_name = upload_file_to_minio(content, file_name)

        file_data: Dict[str, Any] = {
            "file_id": str(uuid.uuid4()),
            "file_name": file.filename,
            "object_name": object_name,
            "file_type": file.content_type,
        }

        # Send file for processing via RabbitMQ
        success = send_file_for_processing(file_data)

        if success:
            return {
                "message": "File uploaded to MinIO and sent for processing",
                "file_id": file_data["file_id"],
            }
        else:
            raise HTTPException(
                status_code=500, detail="Failed to send file for processing"
            )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing file: {str(e)}")
