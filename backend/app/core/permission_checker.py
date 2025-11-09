from typing import Optional
from fastapi import Depends, HTTPException, status
from sqlmodel import Session
from app.database.session import get_session
from app.core.auth import get_current_user
from app.core.security import has_permission
from app.models.user import User


class PermissionChecker:
    def __init__(self, permission_name: str, resource_scope: Optional[str] = None):
        self.permission_name = permission_name
        self.resource_scope = resource_scope

    def __call__(
        self,
        session: Session = Depends(get_session),
        current_user: User = Depends(get_current_user),
    ) -> bool:
        # Assert that authenticated users must have a valid ID
        assert current_user.id is not None, "Authenticated user must have a valid ID"

        if not has_permission(
            session, current_user.id, self.permission_name, self.resource_scope
        ):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Permission '{self.permission_name}' required",
            )
        return True
