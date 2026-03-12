from fastapi import FastAPI
from app.upload import router as upload_router
app = FastAPI(title="Plagiarism Detection File Processor")

app.include_router(upload_router,prefix="/api")

@app.get("/")
def root():
    return {"status": "running"}