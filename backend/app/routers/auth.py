from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session
from app.database.session import get_session
from app.core.auth import authenticate_user, create_user_access_token
from app.schemas.token import (
    Token,
    LoginRequest,
    PasswordResetRequest,
    PasswordResetConfirm,
)
from app.core.user_service import get_user_by_email, get_user_by_username, create_user
from app.models.user import UserCreate
import secrets

router = APIRouter()

# In a real application, you would use a proper database to store reset tokens
# This is just a simple in-memory store for demonstration
reset_tokens = {}


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


@router.post("/forgot-password")
def forgot_password(
    reset_request: PasswordResetRequest, session: Session = Depends(get_session)
):
    user = get_user_by_email(session, reset_request.email)
    if not user:
        # We don't reveal if the email exists or not for security reasons
        return {"message": "If the email exists, a reset link has been sent"}

    # Generate a secure reset token
    token = secrets.token_urlsafe(32)
    reset_tokens[token] = reset_request.email

    # In a real application, you would send an email with the reset link
    # For now, we'll just return the token
    return {"message": "Reset token generated", "token": token}


@router.post("/reset-password")
def reset_password(
    reset_confirm: PasswordResetConfirm, session: Session = Depends(get_session)
):
    email = reset_tokens.get(reset_confirm.token)
    if not email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid or expired token"
        )

    user = get_user_by_email(session, email)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )

    # Update user's password
    # In a real application, you would hash the password here
    # user.hashed_password = get_password_hash(reset_confirm.new_password)
    # session.add(user)
    # session.commit()

    # Remove the used token
    del reset_tokens[reset_confirm.token]

    return {"message": "Password reset successfully"}
