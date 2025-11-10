from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List, TYPE_CHECKING
from datetime import datetime
from app.models.enums import SubmissionStatus
import sqlalchemy.dialects.postgresql as pg

if TYPE_CHECKING:
    from app.models.user import User, Student
    from app.models.topic import Topic


class SubmissionBase(SQLModel):
    topic_id: int = Field(foreign_key="topic.id")
    student_id: int = Field(foreign_key="user.id")
    file_name: str = Field(max_length=500)
    file_path: str = Field(max_length=1000)
    file_size: int
    file_hash: Optional[str] = Field(default=None, max_length=64)
    status: SubmissionStatus = Field(default=SubmissionStatus.SUBMITTED)
    plagiarism_score: Optional[float] = Field(default=None, ge=0, le=100)
    plagiarism_report: Optional[dict] = Field(default=None, sa_type=pg.JSONB)


class Submission(SubmissionBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    submitted_at: datetime = Field(default_factory=datetime.utcnow)
    checked_at: Optional[datetime] = None

    # Relationships
    topic: "Topic" = Relationship(
        back_populates="submissions", sa_relationship_kwargs={"lazy": "selectin"}
    )
    student: "User" = Relationship(
        sa_relationship_kwargs={
            "foreign_keys": "Submission.student_id",
            "lazy": "selectin",
        }
    )
    student_profile: Optional["Student"] = Relationship(
        sa_relationship_kwargs={
            "primaryjoin": "and_(foreign(Submission.student_id) == Student.user_id)",
            "viewonly": True,
            "lazy": "selectin",
        }
    )
    histories: List["SubmissionHistory"] = Relationship(
        back_populates="submission", sa_relationship_kwargs={"lazy": "selectin"}
    )  # type: ignore


class SubmissionCreate(SubmissionBase):
    pass


class SubmissionUpdate(SQLModel):
    status: Optional[SubmissionStatus] = None
    plagiarism_score: Optional[float] = None
    plagiarism_report: Optional[dict] = None
    checked_at: Optional[datetime] = None


class SubmissionHistoryBase(SQLModel):
    submission_id: Optional[int] = Field(default=None, foreign_key="submission.id")
    topic_id: int = Field(foreign_key="topic.id")
    student_id: int = Field(foreign_key="user.id")
    file_name: str = Field(max_length=500)
    file_path: str = Field(max_length=1000)
    file_size: int
    file_hash: Optional[str] = Field(default=None, max_length=64)
    action: str = Field(max_length=50)
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None


class SubmissionHistory(SubmissionHistoryBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    submission: Optional["Submission"] = Relationship(
        back_populates="histories", sa_relationship_kwargs={"lazy": "selectin"}
    )  # type: ignore
    topic: "Topic" = Relationship(sa_relationship_kwargs={"lazy": "selectin"})
    student: "User" = Relationship(
        sa_relationship_kwargs={
            "foreign_keys": "SubmissionHistory.student_id",
            "lazy": "selectin",
        }
    )
