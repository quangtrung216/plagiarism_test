from fastapi import FastAPI
from app.upload import router as upload_router
from app.check import router as check_router
from app.subjects import router as subjects_router
from app.preprocess import router as preprocess_router
from app.test_extract_sentences import router as test_extract_router
app = FastAPI(title="Plagiarism Detection File Processor")

app.include_router(upload_router,prefix="/api")
app.include_router(check_router,prefix="/api")
app.include_router(subjects_router,prefix="/api")
app.include_router(preprocess_router,prefix="/api")
app.include_router(test_extract_router,prefix="/api")

@app.get("/")
def root():
    return {"status": "running"}