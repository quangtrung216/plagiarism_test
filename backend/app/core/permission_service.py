from typing import List, Optional
from sqlmodel import Session, select, col
from app.models.permission import (
    Permission,
    PermissionBase,
    Role,
    RoleBase,
    RolePermission,
    UserRoleAssignment,
    UserRoleAssignmentBase,
    SYSTEM_PERMISSIONS,
    SYSTEM_ROLES,
)
from app.models.user import User


class PermissionService:
    """Service for managing permissions and roles"""

    def __init__(self, session: Session):
        self.session = session

    def initialize_system_permissions(self) -> None:
        """Initialize system permissions and roles"""
        # Check if permissions already exist
        existing_permissions = list(self.session.exec(select(Permission)).all())
        if not existing_permissions:
            # Create system permissions
            for perm_data in SYSTEM_PERMISSIONS:
                permission = Permission(**perm_data)
                self.session.add(permission)

        # Check if roles already exist
        existing_roles = list(self.session.exec(select(Role)).all())
        if not existing_roles:
            # Create system roles
            for role_data in SYSTEM_ROLES:
                role = Role(**role_data)
                self.session.add(role)

        self.session.commit()

        # Assign permissions to roles if not already done
        self._assign_default_permissions()

    def _assign_default_permissions(self) -> None:
        """Assign default permissions to system roles"""
        # Get roles
        student_role = self.session.exec(
            select(Role).where(Role.name == "student")
        ).first()
        teacher_role = self.session.exec(
            select(Role).where(Role.name == "teacher")
        ).first()
        admin_role = self.session.exec(select(Role).where(Role.name == "admin")).first()

        if not student_role or not teacher_role or not admin_role:
            return

        # Assign permissions to student role
        if student_role:
            self._assign_student_permissions(student_role)

        # Assign permissions to teacher role
        if teacher_role:
            self._assign_teacher_permissions(teacher_role)

        # Assign permissions to admin role
        if admin_role:
            self._assign_admin_permissions(admin_role)

        self.session.commit()

    def _assign_student_permissions(self, role: Role) -> None:
        """Assign default permissions to student role"""
        # Get student permissions
        permission_names = [
            "view_topic",
            "submit_assignment",
            "view_submission",
            "view_user",
            "view_documents",  # Students can view documents
        ]

        permissions = list(
            self.session.exec(
                select(Permission).where(col(Permission.name).in_(permission_names))
            ).all()
        )

        # Assign permissions to role
        for permission in permissions:
            assert role.id is not None, "Role ID cannot be None"
            assert permission.id is not None, "Permission ID cannot be None"
            role_permission = RolePermission(
                role_id=role.id, permission_id=permission.id
            )
            self.session.add(role_permission)

    def _assign_teacher_permissions(self, role: Role) -> None:
        """Assign default permissions to teacher role"""
        # Get teacher permissions
        permission_names = [
            "create_topic",
            "view_topic",
            "edit_topic",
            "delete_topic",
            "manage_topic_members",
            "view_submission",
            "grade_submission",
            "delete_submission",
            "view_user",
            "edit_user",
            "view_documents",  # Teachers can view documents
            "manage_documents",  # Teachers can manage documents
        ]

        permissions = list(
            self.session.exec(
                select(Permission).where(col(Permission.name).in_(permission_names))
            ).all()
        )

        # Assign permissions to role
        for permission in permissions:
            assert role.id is not None, "Role ID cannot be None"
            assert permission.id is not None, "Permission ID cannot be None"
            role_permission = RolePermission(
                role_id=role.id, permission_id=permission.id
            )
            self.session.add(role_permission)

    def _assign_admin_permissions(self, role: Role) -> None:
        """Assign all permissions to admin role"""
        permissions = list(self.session.exec(select(Permission)).all())

        # Assign all permissions to role
        for permission in permissions:
            # Check if this assignment already exists
            assert role.id is not None, "Role ID cannot be None"
            assert permission.id is not None, "Permission ID cannot be None"
            existing = self.session.exec(
                select(RolePermission)
                .where(RolePermission.role_id == role.id)
                .where(RolePermission.permission_id == permission.id)
            ).first()

            if not existing:
                role_permission = RolePermission(
                    role_id=role.id, permission_id=permission.id
                )
                self.session.add(role_permission)

    def create_permission(self, permission_data: PermissionBase) -> Permission:
        """Create a new permission"""
        permission = Permission(**permission_data.dict())
        self.session.add(permission)
        self.session.commit()
        self.session.refresh(permission)
        return permission

    def get_permission(self, permission_id: int) -> Optional[Permission]:
        """Get a permission by ID"""
        return self.session.get(Permission, permission_id)

    def get_permissions(self) -> List[Permission]:
        """Get all permissions"""
        return list(self.session.exec(select(Permission)).all())

    def update_permission(
        self, permission_id: int, permission_data: PermissionBase
    ) -> Optional[Permission]:
        """Update a permission"""
        permission = self.session.get(Permission, permission_id)
        if not permission:
            return None

        for key, value in permission_data.dict().items():
            setattr(permission, key, value)

        self.session.add(permission)
        self.session.commit()
        self.session.refresh(permission)
        return permission

    def delete_permission(self, permission_id: int) -> bool:
        """Delete a permission"""
        permission = self.session.get(Permission, permission_id)
        if not permission:
            return False

        self.session.delete(permission)
        self.session.commit()
        return True

    def create_role(self, role_data: RoleBase) -> Role:
        """Create a new role"""
        role = Role(**role_data.dict())
        self.session.add(role)
        self.session.commit()
        self.session.refresh(role)
        return role

    def get_role(self, role_id: int) -> Optional[Role]:
        """Get a role by ID"""
        return self.session.get(Role, role_id)

    def get_roles(self) -> List[Role]:
        """Get all roles"""
        return list(self.session.exec(select(Role)).all())

    def get_role_by_name(self, name: str) -> Optional[Role]:
        """Get a role by name"""
        return self.session.exec(select(Role).where(Role.name == name)).first()

    def update_role(self, role_id: int, role_data: RoleBase) -> Optional[Role]:
        """Update a role"""
        role = self.session.get(Role, role_id)
        if not role:
            return None

        for key, value in role_data.dict().items():
            setattr(role, key, value)

        self.session.add(role)
        self.session.commit()
        self.session.refresh(role)
        return role

    def delete_role(self, role_id: int) -> bool:
        """Delete a role"""
        role = self.session.get(Role, role_id)
        if not role:
            return False

        self.session.delete(role)
        self.session.commit()
        return True

    def assign_role_to_user(
        self, assignment_data: UserRoleAssignmentBase
    ) -> UserRoleAssignment:
        """Assign a role to a user"""
        assignment = UserRoleAssignment(**assignment_data.dict())
        self.session.add(assignment)
        self.session.commit()
        self.session.refresh(assignment)
        return assignment

    def get_user_roles(self, user_id: int) -> List[UserRoleAssignment]:
        """Get all roles assigned to a user"""
        return list(
            self.session.exec(
                select(UserRoleAssignment)
                .where(UserRoleAssignment.user_id == user_id)
                .where(UserRoleAssignment.is_active)
            ).all()
        )

    def revoke_user_role(self, assignment_id: int) -> bool:
        """Revoke a role from a user"""
        assignment = self.session.get(UserRoleAssignment, assignment_id)
        if not assignment:
            return False

        assignment.is_active = False
        self.session.add(assignment)
        self.session.commit()
        return True

    def get_role_permissions(self, role_id: int) -> List[Permission]:
        """Get all permissions assigned to a role"""
        role_permissions = list(
            self.session.exec(
                select(RolePermission).where(RolePermission.role_id == role_id)
            ).all()
        )

        permission_ids = [rp.permission_id for rp in role_permissions]
        if not permission_ids:
            return []

        return list(
            self.session.exec(
                select(Permission).where(col(Permission.id).in_(permission_ids))
            ).all()
        )

    def get_user_permissions(self, user_id: int) -> List[Permission]:
        """Get all permissions for a user based on their roles"""
        # Get user's active role assignments
        role_assignments = list(
            self.session.exec(
                select(UserRoleAssignment)
                .where(UserRoleAssignment.user_id == user_id)
                .where(UserRoleAssignment.is_active)
            ).all()
        )

        if not role_assignments:
            return []

        role_ids = [ra.role_id for ra in role_assignments]

        # Get permissions for all roles
        role_permissions = list(
            self.session.exec(
                select(RolePermission).where(col(RolePermission.role_id).in_(role_ids))
            ).all()
        )

        permission_ids = [rp.permission_id for rp in role_permissions]
        if not permission_ids:
            return []

        return list(
            self.session.exec(
                select(Permission).where(col(Permission.id).in_(permission_ids))
            ).all()
        )

    def check_user_permission(
        self, user_id: int, permission_name: str, resource_scope: Optional[str] = None
    ) -> bool:
        """Check if a user has a specific permission"""
        # Check if user is superuser (has all permissions)
        user = self.session.get(User, user_id)
        if user and user.is_superuser:
            return True

        # Get user's permissions
        permissions = self.get_user_permissions(user_id)

        # Check if user has the required permission
        for permission in permissions:
            if permission.name == permission_name:
                # If a scope is specified, check if it matches
                if resource_scope and permission.scope:
                    if permission.scope == resource_scope:
                        return True
                    # If scope doesn't match, continue checking
                    continue
                # If no scope specified or permission has no scope, it's a match
                return True

        return False

    def assign_permission_to_role(
        self, role_id: int, permission_id: int
    ) -> RolePermission:
        """Assign a permission to a role"""
        # Check if role exists
        role = self.session.get(Role, role_id)
        if not role:
            raise ValueError("Role not found")

        # Check if permission exists
        permission = self.session.get(Permission, permission_id)
        if not permission:
            raise ValueError("Permission not found")

        # Check if this assignment already exists
        existing = self.session.exec(
            select(RolePermission)
            .where(RolePermission.role_id == role_id)
            .where(RolePermission.permission_id == permission_id)
        ).first()

        if existing:
            return existing

        # Create new role-permission assignment
        role_permission = RolePermission(role_id=role_id, permission_id=permission_id)
        self.session.add(role_permission)
        self.session.commit()
        self.session.refresh(role_permission)
        return role_permission

    def revoke_permission_from_role(self, role_id: int, permission_id: int) -> bool:
        """Revoke a permission from a role"""
        # Find the role-permission assignment
        role_permission = self.session.exec(
            select(RolePermission)
            .where(RolePermission.role_id == role_id)
            .where(RolePermission.permission_id == permission_id)
        ).first()

        if not role_permission:
            return False

        self.session.delete(role_permission)
        self.session.commit()
        return True
