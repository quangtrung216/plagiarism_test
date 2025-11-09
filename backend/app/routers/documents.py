from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from sqlmodel import Session
from typing import List, Dict, Any
from app.database.session import get_session
from app.core.auth import get_current_user
from app.core.permission_checker import PermissionChecker
from app.models.user import User
from app.utils.minio_client import (
    upload_file_to_minio,
    delete_file_from_minio,
    list_files_in_minio,
)

router = APIRouter()


@router.post("/upload/", summary="Upload a document")
async def upload_document(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
    check_permission: bool = Depends(PermissionChecker("manage_documents")),
):
    """
    Upload a document to MinIO storage.
    Requires 'manage_documents' permission.
    """
    # Assert that authenticated users must have a valid ID
    assert current_user.id is not None, "Authenticated user must have a valid ID"

    try:
        # Read file content
        content = await file.read()

        # Upload file to MinIO
        file_name = file.filename if file.filename else "unnamed_file"
        object_name = upload_file_to_minio(content, file_name)

        return {
            "message": "Document uploaded successfully",
            "file_name": file_name,
            "object_name": object_name,
            "content_type": file.content_type,
        }
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error uploading document: {str(e)}"
        )


@router.get("/", response_model=List[Dict[str, Any]], summary="List all documents")
def list_documents(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
    check_permission: bool = Depends(PermissionChecker("view_documents")),
):
    """
    List all documents stored in MinIO.
    Requires 'view_documents' permission.
    """
    # Assert that authenticated users must have a valid ID
    assert current_user.id is not None, "Authenticated user must have a valid ID"

    try:
        # List objects in MinIO bucket
        object_list = list_files_in_minio()

        # Apply pagination
        paginated_objects = object_list[skip : skip + limit]

        # Format response
        documents = []
        for obj in paginated_objects:
            documents.append(
                {
                    "object_name": obj.object_name,
                    "size": obj.size,
                    "last_modified": obj.last_modified,
                    "content_type": getattr(obj, "content_type", None),
                }
            )

        return documents
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error listing documents: {str(e)}"
        )


@router.delete("/{object_name}", summary="Delete a document")
def delete_document(
    object_name: str,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
    check_permission: bool = Depends(PermissionChecker("manage_documents")),
):
    """
    Delete a document from MinIO by its object name.
    Requires 'manage_documents' permission.
    """
    # Assert that authenticated users must have a valid ID
    assert current_user.id is not None, "Authenticated user must have a valid ID"

    try:
        # Delete file from MinIO
        success = delete_file_from_minio(object_name)

        if success:
            return {"message": f"Document '{object_name}' deleted successfully"}
        else:
            raise HTTPException(status_code=500, detail="Failed to delete document")
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error deleting document: {str(e)}"
        )


@router.get("/search/", response_model=List[Dict[str, Any]], summary="Search documents")
def search_documents(
    query: str,
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
    check_permission: bool = Depends(PermissionChecker("view_documents")),
):
    """
    Search documents by name in MinIO.
    Requires 'view_documents' permission.
    """
    # Assert that authenticated users must have a valid ID
    assert current_user.id is not None, "Authenticated user must have a valid ID"

    try:
        # List objects in MinIO bucket with prefix filter
        object_list = list_files_in_minio(prefix=query)

        # Apply pagination
        paginated_objects = object_list[skip : skip + limit]

        # Format response
        documents = []
        for obj in paginated_objects:
            documents.append(
                {
                    "object_name": obj.object_name,
                    "size": obj.size,
                    "last_modified": obj.last_modified,
                    "content_type": getattr(obj, "content_type", None),
                }
            )

        return documents
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error searching documents: {str(e)}"
        )
