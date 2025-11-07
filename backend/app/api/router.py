from fastapi import APIRouter
from app.routers import auth, users

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(users.router, prefix="/users", tags=["users"])

# Add other routers here as they are created
# api_router.include_router(documents.router, prefix="/documents", tags=["documents"])
