from sqlmodel import SQLModel, Field, Relationship
from typing import List, Optional, TYPE_CHECKING
from datetime import datetime
import sqlalchemy.dialects.postgresql as pg
import secrets
import string
from pydantic import field_validator

if TYPE_CHECKING:
    from app.models.user import User, Teacher
    from app.models.topic_member import TopicMember
    from app.models.submission import Submission


class TopicBase(SQLModel):
    title: str = Field(max_length=500)
    description: Optional[str] = None
    teacher_id: int = Field(foreign_key="user.id")
    deadline: Optional[datetime] = None
    max_file_size: int = Field(default=10485760)  # 10MB default
    allowed_extensions: List[str] = Field(
        default=["pdf", "doc", "docx", "txt"], sa_type=pg.ARRAY(pg.VARCHAR)
    )
    code: Optional[str] = Field(default=None, max_length=20, unique=True, index=True)
    public: bool = Field(default=False)
    require_approval: bool = Field(default=True)
    max_uploads: Optional[int] = Field(default=1)  # Default to 1 upload
    threshold: Optional[float] = Field(default=0.8)  # Default to 80% threshold


class Topic(TopicBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Generate a unique code before inserting
    def __init__(self, **data):
        if "code" not in data or data["code"] is None:
            data["code"] = self.generate_unique_code()
        super().__init__(**data)

    @staticmethod
    def generate_unique_code(length=8):
        """Generate a unique code for the topic"""
        characters = string.ascii_uppercase + string.digits
        return "".join(secrets.choice(characters) for _ in range(length))

    # Relationships
    teacher: "User" = Relationship(
        back_populates="topics", sa_relationship_kwargs={"lazy": "selectin"}
    )
    teacher_profile: Optional["Teacher"] = Relationship(
        sa_relationship_kwargs={
            "primaryjoin": "and_(foreign(Topic.teacher_id) == Teacher.user_id)",
            "viewonly": True,
            "lazy": "selectin",
        }
    )
    members: List["TopicMember"] = Relationship(
        back_populates="topic", sa_relationship_kwargs={"lazy": "selectin"}
    )
    submissions: List["Submission"] = Relationship(
        back_populates="topic", sa_relationship_kwargs={"lazy": "selectin"}
    )


class TopicCreate(SQLModel):
    title: str = Field(max_length=500)
    description: Optional[str] = None
    deadline: Optional[datetime] = None
    max_file_size: int = Field(default=10485760)  # 10MB default
    allowed_extensions: List[str] = Field(
        default=["pdf", "doc", "docx", "txt"], sa_type=pg.ARRAY(pg.VARCHAR)
    )
    code: Optional[str] = Field(default=None, max_length=20, unique=True, index=True)
    public: bool = Field(default=False)
    require_approval: bool = Field(default=True)
    max_uploads: Optional[int] = Field(default=1)  # Default to 1 upload
    threshold: Optional[float] = Field(default=0.8)  # Default to 80% threshold

    @field_validator("deadline", mode="before")
    @classmethod
    def empty_deadline_is_none(cls, v):
        """Convert empty string to None for deadline field"""
        if v == "":
            return None
        return v


class TopicUpdate(SQLModel):
    title: Optional[str] = None
    description: Optional[str] = None
    deadline: Optional[datetime] = None
    max_file_size: Optional[int] = None
    allowed_extensions: Optional[List[str]] = None
    code: Optional[str] = None
    public: Optional[bool] = None
    require_approval: Optional[bool] = None
    max_uploads: Optional[int] = None
    threshold: Optional[float] = None

    @field_validator("deadline", mode="before")
    @classmethod
    def empty_deadline_is_none(cls, v):
        """Convert empty string to None for deadline field"""
        if v == "":
            return None
        return v
