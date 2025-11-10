from sqlmodel import SQLModel, Field, Relationship
from typing import List, Optional, TYPE_CHECKING
from datetime import datetime
from app.models.enums import TopicStatus
import sqlalchemy.dialects.postgresql as pg

if TYPE_CHECKING:
    from app.models.user import User, Teacher
    from app.models.topic_member import TopicMember
    from app.models.submission import Submission


class TopicBase(SQLModel):
    title: str = Field(max_length=500)
    description: Optional[str] = None
    teacher_id: int = Field(foreign_key="user.id")
    status: TopicStatus = Field(default=TopicStatus.DRAFT)
    deadline: Optional[datetime] = None
    max_file_size: int = Field(default=10485760)  # 10MB default
    allowed_extensions: List[str] = Field(
        default=["pdf", "doc", "docx", "txt"], sa_type=pg.ARRAY(pg.VARCHAR)
    )


class Topic(TopicBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

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


class TopicCreate(TopicBase):
    pass


class TopicUpdate(SQLModel):
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[TopicStatus] = None
    deadline: Optional[datetime] = None
    max_file_size: Optional[int] = None
    allowed_extensions: Optional[List[str]] = None
