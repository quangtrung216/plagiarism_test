from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, TYPE_CHECKING
from datetime import datetime
from app.models.enums import MemberStatus

if TYPE_CHECKING:
    from app.models.user import User, Student
    from app.models.topic import Topic


class TopicMemberBase(SQLModel):
    topic_id: int = Field(foreign_key="topic.id")
    student_id: int = Field(foreign_key="user.id")
    status: MemberStatus = Field(default=MemberStatus.PENDING)
    note: Optional[str] = None


class TopicMember(TopicMemberBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    requested_at: datetime = Field(default_factory=datetime.utcnow)
    responded_at: Optional[datetime] = None
    responded_by: Optional[int] = Field(default=None, foreign_key="user.id")

    # Relationships
    topic: "Topic" = Relationship(
        back_populates="members", sa_relationship_kwargs={"lazy": "selectin"}
    )
    student: "User" = Relationship(
        back_populates="topic_memberships",
        sa_relationship_kwargs={
            "foreign_keys": "TopicMember.student_id",
            "lazy": "selectin",
        },
    )
    responder: Optional["User"] = Relationship(
        sa_relationship_kwargs={
            "foreign_keys": "TopicMember.responded_by",
            "lazy": "selectin",
        }
    )
    student_profile: Optional["Student"] = Relationship(
        sa_relationship_kwargs={
            "primaryjoin": "and_(foreign(TopicMember.student_id) == Student.user_id)",
            "viewonly": True,
            "lazy": "selectin",
        }
    )


class TopicMemberCreate(TopicMemberBase):
    pass


class TopicMemberUpdate(SQLModel):
    status: Optional[MemberStatus] = None
    note: Optional[str] = None
    responded_at: Optional[datetime] = None
    responded_by: Optional[int] = None
