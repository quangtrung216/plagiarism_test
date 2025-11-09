from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from sqlmodel import Session
from app.database.session import get_session
from app.core.auth import get_current_user
from app.core.permission_checker import PermissionChecker
from app.models.user import User

router = APIRouter(prefix="/file-upload", tags=["file upload"])


@router.post("/upload/")
async def upload_file(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
    permission_check: bool = Depends(PermissionChecker("manage_documents")),
):
    """
    Example endpoint for uploading a file with permission checking.
    Requires 'manage_documents' permission.
    """
    # Assert that authenticated users must have a valid ID
    assert current_user.id is not None, "Authenticated user must have a valid ID"

    try:
        # In a real implementation, you would save the file to storage
        content = await file.read()
        file_size = len(content)

        return {
            "filename": file.filename,
            "content_type": file.content_type,
            "size": file_size,
            "message": "File uploaded successfully",
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error uploading file: {str(e)}")
