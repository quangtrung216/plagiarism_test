from fastapi import APIRouter, UploadFile, File, Form
from typing import List, Optional
from model.doc import UploadBatchResponse
from services.upload_service import handle_upload, handle_upload_batch, handle_upload_doc

router = APIRouter()

@router.post("/upload-pdf")
async def upload_pdf(file: UploadFile = File(...), subject_id: str = Form(...), document_type: str = Form(default="none")):
    if not file.filename.lower().endswith((".pdf", ".docx")):
        return {"error": "Only PDF and DOCX files are allowed."}
    doc = await handle_upload_doc(file, subject_id=subject_id, document_type=document_type)
    return {
        "document_id": doc.document_id,
        "file_name": doc.file_name,
        "subject_id": doc.subject_id,
        "file_path": doc.file_path
    }

@router.post("/upload", response_model=UploadBatchResponse)
async def upload_files(
    files: List[UploadFile] = File(...),
    subject_id: str = Form(...),
    document_type: str = Form(default="none"),
    language: Optional[str] = Form(default="vi"),
):
    return await handle_upload_batch(
        files=files,
        subject_id=subject_id,
        document_type=document_type,
        language=language,
    )