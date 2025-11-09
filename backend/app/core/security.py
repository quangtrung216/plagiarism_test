from typing import Optional
from datetime import datetime, timedelta
from jose import jwt
from sqlmodel import Session, select
from app.core.config import settings
from app.models.user import User
from app.core.permission_service import PermissionService
import bcrypt
from fastapi import HTTPException, status


# JWT
ALGORITHM = "HS256"


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plain password against a hashed password"""
    # Convert the hashed_password from string to bytes
    hashed_bytes = hashed_password.encode("utf-8")
    # Convert the plain_password to bytes
    plain_bytes = plain_password.encode("utf-8")
    # Verify the password
    return bcrypt.checkpw(plain_bytes, hashed_bytes)


def get_password_hash(password: str) -> str:
    """Hash a password using bcrypt"""
    # Ensure password is not longer than 72 bytes to avoid truncation issues
    if len(password.encode("utf-8")) > 72:
        raise ValueError("Password cannot be longer than 72 bytes")

    # Convert password to bytes
    password_bytes = password.encode("utf-8")
    # Generate salt and hash the password
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password_bytes, salt)
    # Return as string
    return hashed.decode("utf-8")


def authenticate_user(session: Session, username: str, password: str) -> Optional[User]:
    """Authenticate a user by username and password"""
    statement = select(User).where(User.username == username)
    user = session.exec(statement).first()
    if not user or not verify_password(password, user.hashed_password):
        return None
    return user


def create_access_token(subject: str, expires_delta: Optional[timedelta] = None) -> str:
    """Create a JWT access token"""
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )

    to_encode = {"exp": expire, "sub": str(subject)}
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def has_permission(
    session: Session,
    user_id: int,
    permission_name: str,
    resource_scope: Optional[str] = None,
) -> bool:
    """Check if a user has a specific permission"""
    permission_service = PermissionService(session)
    return permission_service.check_user_permission(
        user_id, permission_name, resource_scope
    )


def require_permission(permission_name: str, resource_scope: Optional[str] = None):
    """Decorator to require a specific permission for an endpoint"""

    def decorator(func):
        def wrapper(*args, **kwargs):
            # Extract session and current user from function arguments
            # This assumes the session and current_user are passed as dependencies
            session = kwargs.get("session")
            current_user = kwargs.get("current_user")

            if not session or not current_user:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Authentication required",
                )

            # Assert that authenticated users must have a valid ID
            assert (
                current_user.id is not None
            ), "Authenticated user must have a valid ID"

            # Check if user has the required permission
            if not has_permission(
                session, current_user.id, permission_name, resource_scope
            ):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Permission '{permission_name}' required",
                )

            return func(*args, **kwargs)

        # Preserve the original function signature for FastAPI dependency injection
        import functools

        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs):
            # Extract session and current user from function arguments
            session = kwargs.get("session")
            current_user = kwargs.get("current_user")

            if not session or not current_user:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Authentication required",
                )

            # Assert that authenticated users must have a valid ID
            assert (
                current_user.id is not None
            ), "Authenticated user must have a valid ID"

            # Check if user has the required permission
            if not has_permission(
                session, current_user.id, permission_name, resource_scope
            ):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Permission '{permission_name}' required",
                )

            return await func(*args, **kwargs)

        # Return the appropriate wrapper based on whether the original function is async
        import asyncio

        return async_wrapper if asyncio.iscoroutinefunction(func) else wrapper

    return decorator
