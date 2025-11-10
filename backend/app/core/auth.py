from typing import Any, Optional
from sqlmodel import select, Session
from app.models.user import User
from app.core.security import verify_password, create_access_token
from jose import JWTError, jwt
from app.core.config import settings
from fastapi import HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.database.session import get_session
import json

# Create HTTPBearer instance for JWT
security = HTTPBearer()


def authenticate_user(session, username: str, password: str) -> Optional[User]:
    statement = select(User).where(User.username == username)
    user = session.exec(statement).first()

    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user


def create_user_access_token(user: User) -> str:
    return create_access_token(str(user.id))  # Pass user ID as string subject


def get_current_user(
    session: Session = Depends(get_session),
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> Optional[User]:
    try:
        payload = jwt.decode(
            credentials.credentials, settings.SECRET_KEY, algorithms=["HS256"]
        )
        user_id_str: Any | None = payload.get("sub")
        if user_id_str is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )

        # Xử lý trường hợp user_id_str là chuỗi JSON
        try:
            # Thử parse nếu nó là chuỗi JSON
            user_data = json.loads(user_id_str)
            if isinstance(user_data, dict):
                user_id = user_data.get("sub")
            else:
                user_id = user_id_str
        except (json.JSONDecodeError, TypeError):
            # Nếu không phải JSON, sử dụng trực tiếp
            user_id = user_id_str

        # Kiểm tra user_id không phải None trước khi chuyển thành số nguyên
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid user ID in token",
                headers={"WWW-Authenticate": "Bearer"},
            )

        # Chuyển user_id thành số nguyên nếu có thể
        try:
            user_id = int(user_id)
        except (ValueError, TypeError):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid user ID in token",
                headers={"WWW-Authenticate": "Bearer"},
            )
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Tìm user theo ID thay vì username
    statement = select(User).where(User.id == user_id)
    user = session.exec(statement).first()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user
