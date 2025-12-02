from sqlmodel import SQLModel, Field, Relationship
from datetime import datetime
from typing import Optional, List, TYPE_CHECKING
from enum import Enum

if TYPE_CHECKING:
    from app.models.topic import Topic
    from app.models.topic_member import TopicMember
    from app.models.submission import Submission

    # Added permission models
    from app.models.permission import UserRoleAssignment


class UserRole(str, Enum):
    STUDENT = "student"
    TEACHER = "teacher"
    ADMIN = "admin"


class UserBase(SQLModel):
    username: str = Field(unique=True, index=True, max_length=50)
    email: str = Field(unique=True, index=True)
    is_active: bool = True
    is_superuser: bool = False
    full_name: Optional[str] = None
    role: UserRole


class User(UserBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    hashed_password: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    topics: List["Topic"] = Relationship(
        back_populates="teacher", sa_relationship_kwargs={"lazy": "selectin"}
    )
    topic_memberships: List["TopicMember"] = Relationship(
        back_populates="student",
        sa_relationship_kwargs={
            "foreign_keys": "TopicMember.student_id",
            "lazy": "selectin",
        },
    )
    submissions: List["Submission"] = Relationship(
        back_populates="student",
        sa_relationship_kwargs={
            "foreign_keys": "Submission.student_id",
            "lazy": "selectin",
        },
    )

    # Role-specific relationships (optional based on user role)
    teacher_profile: Optional["Teacher"] = Relationship(
        back_populates="user", sa_relationship_kwargs={"lazy": "selectin"}
    )
    student_profile: Optional["Student"] = Relationship(
        back_populates="user", sa_relationship_kwargs={"lazy": "selectin"}
    )

    # Permission system relationships
    assigned_roles: List["UserRoleAssignment"] = Relationship(
        back_populates="user",
        sa_relationship_kwargs={
            "foreign_keys": "UserRoleAssignment.user_id",
            "lazy": "selectin",
        },
    )


class UserCreate(UserBase):
    password: str


class UserUpdate(UserBase):
    password: Optional[str] = None


class UserProfileUpdate(SQLModel):
    full_name: Optional[str] = None


class UserOut(UserBase):
    id: int
    created_at: datetime
    updated_at: datetime


class UserInDB(SQLModel):
    id: int
    username: str
    email: str
    is_active: bool
    is_superuser: bool
    full_name: Optional[str]
    role: UserRole
    hashed_password: str
    created_at: datetime
    updated_at: datetime


# Teacher-specific model
class Teacher(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id", unique=True)
    department: Optional[str] = None
    qualification: Optional[str] = None
    specialization: Optional[str] = None
    employee_id: Optional[str] = None  # Staff ID or employee number
    hire_date: Optional[datetime] = None

    # Relationships
    user: "User" = Relationship(
        back_populates="teacher_profile", sa_relationship_kwargs={"lazy": "selectin"}
    )


# Student-specific model
class Student(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id", unique=True)
    student_id: str = Field(unique=True)  # Student enrollment number
    major: Optional[str] = None
    year: Optional[int] = None
    semester: Optional[int] = None
    enrollment_date: Optional[datetime] = None
    graduation_date: Optional[datetime] = None

    # Relationships
    user: "User" = Relationship(
        back_populates="student_profile", sa_relationship_kwargs={"lazy": "selectin"}
    )
