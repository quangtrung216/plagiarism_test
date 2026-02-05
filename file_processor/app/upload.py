from fastapi import APIRouter, UploadFile, File
from services.upload_service import handle_upload

router = APIRouter()

@router.post("/upload-pdf")
async def upload_pdf(file: UploadFile = File(...)):
    if not file.filename.lower().endswith(".pdf"):
        return {"error": "Only PDF files are allowed."}
    doc_id = await handle_upload(file)
    return {
        "message": "File uploaded successfully.",
        "document_id": doc_id
    }