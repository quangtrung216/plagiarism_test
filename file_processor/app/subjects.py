from fastapi import APIRouter
from services.subject_service import get_all_subjects, get_subject_by_id, create_subject

router = APIRouter()

@router.get("/subjects")
async def list_subjects():
    """Get all available subjects"""
    subjects = get_all_subjects()
    return {"subjects": subjects}

@router.get("/subjects/{subject_id}")
async def get_subject(subject_id: str):
    """Get a specific subject by ID"""
    subject = get_subject_by_id(subject_id)
    if not subject:
        return {"error": "Subject not found"}
    return subject

@router.post("/subjects")
async def add_subject(subject_id: str, subject_name: str, description: str = None):
    """Create a new subject"""
    try:
        subject = create_subject(subject_id, subject_name, description)
        return {"message": "Subject created successfully", "subject": subject}
    except Exception as e:
        return {"error": f"Failed to create subject: {str(e)}"}
