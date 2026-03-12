from fastapi import APIRouter, File, UploadFile, Form

from services.check_service import handle_check

router = APIRouter()


@router.post("/check-plagiarism")
async def check_plagiarism(
    file: UploadFile = File(...), 
    subject_id: str = Form(default=""), 
    document_type: str = Form(default="")
):
    if not file.filename.lower().endswith(".pdf"):
        return {"error": "Only PDF files are allowed."}
    return await handle_check(file, subject_id=subject_id, document_type=document_type)
