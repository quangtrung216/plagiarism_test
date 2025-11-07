from typing import Optional
from sqlmodel import select, Session
from app.models.user import User
from app.core.security import verify_password, create_access_token
from app.schemas.token import TokenData
from jose import JWTError, jwt
from app.core.config import settings
from fastapi import HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.database.session import get_session

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
    data = {"sub": user.username, "user_id": user.id}
    return create_access_token(data)


def get_current_user(
    session: Session = Depends(get_session),
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> Optional[User]:
    try:
        payload = jwt.decode(
            credentials.credentials, settings.SECRET_KEY, algorithms=["HS256"]
        )
        username = payload.get("sub")
        if username is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
        token_data = TokenData(username=username)
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    statement = select(User).where(User.username == token_data.username)
    user = session.exec(statement).first()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user
