from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List, TYPE_CHECKING
from datetime import datetime
from enum import Enum

if TYPE_CHECKING:
    from app.models.user import User


class PermissionType(str, Enum):
    """Enumeration of permission types"""

    READ = "read"
    WRITE = "write"
    DELETE = "delete"
    ADMIN = "admin"


class ResourceType(str, Enum):
    """Enumeration of resource types in the system"""

    TOPIC = "topic"
    SUBMISSION = "submission"
    USER = "user"
    SYSTEM = "system"


class PermissionBase(SQLModel):
    """Base permission model"""

    name: str = Field(max_length=100, description="Permission name")
    description: Optional[str] = Field(
        default=None, max_length=500, description="Permission description"
    )
    resource_type: ResourceType = Field(
        description="Type of resource this permission applies to"
    )
    permission_type: PermissionType = Field(description="Type of permission")
    scope: Optional[str] = Field(
        default=None,
        max_length=100,
        description="Scope of the permission (e.g., specific topic ID, global)",
    )


class Permission(PermissionBase, table=True):
    """Permission model stored in database"""

    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    role_permissions: List["RolePermission"] = Relationship(back_populates="permission")


class RoleBase(SQLModel):
    """Base role model"""

    name: str = Field(unique=True, index=True, max_length=50, description="Role name")
    description: Optional[str] = Field(
        default=None, max_length=500, description="Role description"
    )
    is_system_role: bool = Field(
        default=False, description="Whether this is a system-defined role"
    )


class Role(RoleBase, table=True):
    """Role model stored in database"""

    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    role_permissions: List["RolePermission"] = Relationship(back_populates="role")
    user_roles: List["UserRoleAssignment"] = Relationship(back_populates="role")


class RolePermissionBase(SQLModel):
    """Base model for role-permission relationship"""

    role_id: int = Field(foreign_key="role.id", description="Foreign key to role")
    permission_id: int = Field(
        foreign_key="permission.id", description="Foreign key to permission"
    )


class RolePermission(RolePermissionBase, table=True):
    """Model representing the relationship between roles and permissions"""

    id: Optional[int] = Field(default=None, primary_key=True)

    # Relationships
    role: "Role" = Relationship(back_populates="role_permissions")
    permission: "Permission" = Relationship(back_populates="role_permissions")


class UserRoleAssignmentBase(SQLModel):
    """Base model for user-role assignment"""

    user_id: int = Field(foreign_key="user.id", description="Foreign key to user")
    role_id: int = Field(foreign_key="role.id", description="Foreign key to role")
    granted_by: int = Field(
        foreign_key="user.id", description="ID of user who granted this role"
    )
    scope: Optional[str] = Field(
        default=None,
        max_length=100,
        description="Scope of the role assignment (e.g., specific topic ID)",
    )


class UserRoleAssignment(UserRoleAssignmentBase, table=True):
    """Model representing the assignment of roles to users"""

    id: Optional[int] = Field(default=None, primary_key=True)
    granted_at: datetime = Field(default_factory=datetime.utcnow)
    expires_at: Optional[datetime] = Field(
        default=None, description="When this role assignment expires"
    )
    is_active: bool = Field(
        default=True, description="Whether this role assignment is currently active"
    )

    # Relationships
    user: "User" = Relationship(
        sa_relationship_kwargs={"foreign_keys": "UserRoleAssignment.user_id"}
    )
    role: "Role" = Relationship(back_populates="user_roles")
    granter: "User" = Relationship(
        sa_relationship_kwargs={"foreign_keys": "UserRoleAssignment.granted_by"}
    )


# Predefined system permissions
SYSTEM_PERMISSIONS = [
    # Topic permissions
    {
        "name": "create_topic",
        "description": "Create new topics",
        "resource_type": ResourceType.TOPIC,
        "permission_type": PermissionType.WRITE,
    },
    {
        "name": "view_topic",
        "description": "View topics",
        "resource_type": ResourceType.TOPIC,
        "permission_type": PermissionType.READ,
    },
    {
        "name": "edit_topic",
        "description": "Edit topics",
        "resource_type": ResourceType.TOPIC,
        "permission_type": PermissionType.WRITE,
    },
    {
        "name": "delete_topic",
        "description": "Delete topics",
        "resource_type": ResourceType.TOPIC,
        "permission_type": PermissionType.DELETE,
    },
    {
        "name": "manage_topic_members",
        "description": "Manage topic members",
        "resource_type": ResourceType.TOPIC,
        "permission_type": PermissionType.ADMIN,
    },
    # Submission permissions
    {
        "name": "submit_assignment",
        "description": "Submit assignments",
        "resource_type": ResourceType.SUBMISSION,
        "permission_type": PermissionType.WRITE,
    },
    {
        "name": "view_submission",
        "description": "View submissions",
        "resource_type": ResourceType.SUBMISSION,
        "permission_type": PermissionType.READ,
    },
    {
        "name": "grade_submission",
        "description": "Grade submissions",
        "resource_type": ResourceType.SUBMISSION,
        "permission_type": PermissionType.WRITE,
    },
    {
        "name": "delete_submission",
        "description": "Delete submissions",
        "resource_type": ResourceType.SUBMISSION,
        "permission_type": PermissionType.DELETE,
    },
    # User permissions
    {
        "name": "view_user",
        "description": "View user profiles",
        "resource_type": ResourceType.USER,
        "permission_type": PermissionType.READ,
    },
    {
        "name": "edit_user",
        "description": "Edit user profiles",
        "resource_type": ResourceType.USER,
        "permission_type": PermissionType.WRITE,
    },
    {
        "name": "manage_users",
        "description": "Manage users",
        "resource_type": ResourceType.USER,
        "permission_type": PermissionType.ADMIN,
    },
    # Document permissions
    {
        "name": "view_documents",
        "description": "View documents",
        "resource_type": ResourceType.SYSTEM,
        "permission_type": PermissionType.READ,
    },
    {
        "name": "manage_documents",
        "description": "Manage documents (upload, delete)",
        "resource_type": ResourceType.SYSTEM,
        "permission_type": PermissionType.ADMIN,
    },
    # System permissions
    {
        "name": "access_admin_panel",
        "description": "Access administrative panel",
        "resource_type": ResourceType.SYSTEM,
        "permission_type": PermissionType.ADMIN,
    },
    {
        "name": "manage_permissions",
        "description": "Manage system permissions",
        "resource_type": ResourceType.SYSTEM,
        "permission_type": PermissionType.ADMIN,
    },
    {
        "name": "view_system_logs",
        "description": "View system logs",
        "resource_type": ResourceType.SYSTEM,
        "permission_type": PermissionType.READ,
    },
]

# Predefined system roles
SYSTEM_ROLES = [
    {
        "name": "student",
        "description": "Student role with basic permissions",
        "is_system_role": True,
    },
    {
        "name": "teacher",
        "description": "Teacher role with topic management permissions",
        "is_system_role": True,
    },
    {
        "name": "admin",
        "description": "Administrator role with full system access",
        "is_system_role": True,
    },
]
