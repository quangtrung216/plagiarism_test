from fastapi import FastAPI
from app.upload import router as upload_router
from app.check import router as check_router
from app.subjects import router as subjects_router
app = FastAPI(title="Plagiarism Detection File Processor")

app.include_router(upload_router,prefix="/api")
app.include_router(check_router,prefix="/api")
app.include_router(subjects_router,prefix="/api")

@app.get("/")
def root():
    return {"status": "running"}