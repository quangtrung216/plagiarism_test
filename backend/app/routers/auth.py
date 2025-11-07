from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session
from app.database.session import get_session
from app.core.auth import authenticate_user, create_user_access_token
from app.schemas.token import (
    Token,
    LoginRequest,
)
from app.core.user_service import get_user_by_email, get_user_by_username, create_user
from app.models.user import UserCreate

router = APIRouter()


@router.post("/login", response_model=Token)
def login(login_request: LoginRequest, session: Session = Depends(get_session)):
    user = authenticate_user(session, login_request.username, login_request.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_user_access_token(user)
    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/register", status_code=status.HTTP_201_CREATED)
def register(user_create: UserCreate, session: Session = Depends(get_session)):
    # Check if user already exists by username
    existing_user = get_user_by_username(session, user_create.username)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this username already exists",
        )

    # Also check if email already exists
    existing_user = get_user_by_email(session, user_create.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this email already exists",
        )

    # Create new user
    new_user = create_user(session, user_create)
    return {"message": "User created successfully", "user_id": new_user.id}
