from sqlmodel import SQLModel
from typing import Optional, List
from datetime import datetime


class TeacherInfo(SQLModel):
    """Minimal teacher information for topic responses"""

    id: int
    full_name: Optional[str]
    username: str


class TopicOut(SQLModel):
    """Topic response model that includes teacher information"""

    id: int
    title: Optional[str] = None
    description: Optional[str] = None
    teacher_id: Optional[int] = None
    deadline: Optional[datetime] = None
    max_file_size: Optional[int] = None
    allowed_extensions: Optional[List[str]] = None
    code: Optional[str] = None
    public: Optional[bool] = None
    require_approval: Optional[bool] = None
    max_uploads: Optional[int] = None
    threshold: Optional[float] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    teacher_info: Optional[TeacherInfo] = None
