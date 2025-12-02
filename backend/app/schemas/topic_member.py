from sqlmodel import SQLModel
from datetime import datetime
from typing import Optional
from app.models.enums import MemberStatus


class StudentProfileInfo(SQLModel):
    student_id: str
    major: Optional[str] = None


class StudentInfo(SQLModel):
    id: Optional[int] = None
    username: Optional[str] = None
    full_name: Optional[str] = None
    email: Optional[str] = None
    student_profile: Optional[StudentProfileInfo] = None


class TopicMemberOut(SQLModel):
    id: int
    topic_id: int
    student_id: int
    status: MemberStatus
    note: Optional[str] = None
    requested_at: datetime
    responded_at: Optional[datetime] = None
    responded_by: Optional[int] = None
    student: StudentInfo
