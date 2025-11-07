from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.middleware.logging_middleware import LoggingMiddleware
from app.api.router import api_router
from app.middleware.exception_handler import ExceptionHandlerMiddleware

app = FastAPI(
    title=settings.PROJECT_NAME, openapi_url=f"{settings.PREFIX}/openapi.json"
)

# Add middlewares
app.add_middleware(ExceptionHandlerMiddleware)
app.add_middleware(LoggingMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(api_router, prefix=settings.PREFIX)


@app.get("/")
async def root():
    return {"message": "Welcome to Plagiarism Detection API"}


@app.get("/health")
async def health_check():
    return {"status": "healthy"}
