from fastapi import APIRouter
from app.routers import auth, users, documents, permissions, file_upload
from app.examples.permission_example import router as example_router

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(documents.router, prefix="/documents", tags=["documents"])
api_router.include_router(
    permissions.router, prefix="/permissions", tags=["permissions"]
)
api_router.include_router(
    file_upload.router, prefix="/file-upload", tags=["file upload"]
)
api_router.include_router(example_router, prefix="/examples", tags=["examples"])
