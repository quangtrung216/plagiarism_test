from fastapi import APIRouter, UploadFile, File, Form
from services.upload_service import handle_upload

router = APIRouter()

@router.post("/upload-pdf")
async def upload_pdf(file: UploadFile = File(...), subject_id: str = Form(...), document_type: str = Form(default="none")):
    if not file.filename.lower().endswith(".pdf"):
        return {"error": "Only PDF files are allowed."}
    doc_id = await handle_upload(file, subject_id=subject_id, document_type=document_type)
    return {
        "message": "File uploaded successfully.",
        "document_id": doc_id
    }