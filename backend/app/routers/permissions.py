from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session

from app.database.session import get_session
from app.models.permission import (
    Permission,
    PermissionBase,
    Role,
    RoleBase,
    RolePermission,
    UserRoleAssignment,
    UserRoleAssignmentBase,
)
from app.core.permission_service import PermissionService
from app.models.user import User
from app.core.auth import get_current_user

router = APIRouter(prefix="/permissions", tags=["permissions"])


@router.post("/permissions/", response_model=Permission)
def create_permission(
    *,
    session: Session = Depends(get_session),
    permission_data: PermissionBase,
    current_user: User = Depends(get_current_user),
):
    """Create a new permission"""
    # In a real implementation, check if user has permission to create permissions
    permission_service = PermissionService(session)
    return permission_service.create_permission(permission_data)


@router.get("/permissions/", response_model=List[Permission])
def read_permissions(
    *,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    """Get all permissions"""
    permission_service = PermissionService(session)
    return permission_service.get_permissions()


@router.get("/permissions/{permission_id}", response_model=Permission)
def read_permission(
    *,
    permission_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    """Get a specific permission by ID"""
    permission_service = PermissionService(session)
    permission = permission_service.get_permission(permission_id)
    if not permission:
        raise HTTPException(status_code=404, detail="Permission not found")
    return permission


@router.put("/permissions/{permission_id}", response_model=Permission)
def update_permission(
    *,
    permission_id: int,
    session: Session = Depends(get_session),
    permission_data: PermissionBase,
    current_user: User = Depends(get_current_user),
):
    """Update a permission"""
    permission_service = PermissionService(session)
    permission = permission_service.update_permission(permission_id, permission_data)
    if not permission:
        raise HTTPException(status_code=404, detail="Permission not found")
    return permission


@router.delete("/permissions/{permission_id}")
def delete_permission(
    *,
    permission_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    """Delete a permission"""
    permission_service = PermissionService(session)
    success = permission_service.delete_permission(permission_id)
    if not success:
        raise HTTPException(status_code=404, detail="Permission not found")
    return {"message": "Permission deleted successfully"}


@router.post("/roles/", response_model=Role)
def create_role(
    *,
    session: Session = Depends(get_session),
    role_data: RoleBase,
    current_user: User = Depends(get_current_user),
):
    """Create a new role"""
    permission_service = PermissionService(session)
    return permission_service.create_role(role_data)


@router.get("/roles/", response_model=List[Role])
def read_roles(
    *,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    """Get all roles"""
    permission_service = PermissionService(session)
    return permission_service.get_roles()


@router.get("/roles/{role_id}", response_model=Role)
def read_role(
    *,
    role_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    """Get a specific role by ID"""
    permission_service = PermissionService(session)
    role = permission_service.get_role(role_id)
    if not role:
        raise HTTPException(status_code=404, detail="Role not found")
    return role


@router.put("/roles/{role_id}", response_model=Role)
def update_role(
    *,
    role_id: int,
    session: Session = Depends(get_session),
    role_data: RoleBase,
    current_user: User = Depends(get_current_user),
):
    """Update a role"""
    permission_service = PermissionService(session)
    role = permission_service.update_role(role_id, role_data)
    if not role:
        raise HTTPException(status_code=404, detail="Role not found")
    return role


@router.delete("/roles/{role_id}")
def delete_role(
    *,
    role_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    """Delete a role"""
    permission_service = PermissionService(session)
    success = permission_service.delete_role(role_id)
    if not success:
        raise HTTPException(status_code=404, detail="Role not found")
    return {"message": "Role deleted successfully"}


@router.post("/role-assignments/", response_model=UserRoleAssignment)
def assign_role_to_user(
    *,
    session: Session = Depends(get_session),
    assignment_data: UserRoleAssignmentBase,
    current_user: User = Depends(get_current_user),
):
    """Assign a role to a user"""
    permission_service = PermissionService(session)
    return permission_service.assign_role_to_user(assignment_data)


@router.get("/users/{user_id}/roles/", response_model=List[UserRoleAssignment])
def get_user_roles(
    *,
    user_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    """Get all roles assigned to a user"""
    permission_service = PermissionService(session)
    return permission_service.get_user_roles(user_id)


@router.delete("/role-assignments/{assignment_id}")
def revoke_user_role(
    *,
    assignment_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    """Revoke a role from a user"""
    permission_service = PermissionService(session)
    success = permission_service.revoke_user_role(assignment_id)
    if not success:
        raise HTTPException(status_code=404, detail="Role assignment not found")
    return {"message": "Role revoked successfully"}


@router.get("/roles/{role_id}/permissions/", response_model=List[Permission])
def get_role_permissions(
    *,
    role_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    """Get all permissions assigned to a role"""
    permission_service = PermissionService(session)
    return permission_service.get_role_permissions(role_id)


@router.post("/role-permissions/", response_model=RolePermission)
def assign_permission_to_role(
    *,
    session: Session = Depends(get_session),
    role_id: int,
    permission_id: int,
    current_user: User = Depends(get_current_user),
):
    """Assign a permission to a role"""
    permission_service = PermissionService(session)
    return permission_service.assign_permission_to_role(role_id, permission_id)


@router.delete("/role-permissions/")
def revoke_permission_from_role(
    *,
    session: Session = Depends(get_session),
    role_id: int,
    permission_id: int,
    current_user: User = Depends(get_current_user),
):
    """Revoke a permission from a role"""
    permission_service = PermissionService(session)
    success = permission_service.revoke_permission_from_role(role_id, permission_id)
    if not success:
        raise HTTPException(
            status_code=404, detail="Role-permission assignment not found"
        )
    return {"message": "Permission revoked from role successfully"}


@router.get("/users/{user_id}/permissions/", response_model=List[Permission])
def get_user_permissions(
    *,
    user_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    """Get all permissions for a user"""
    permission_service = PermissionService(session)
    return permission_service.get_user_permissions(user_id)
