from typing import List, Optional
from datetime import datetime
from sqlmodel import select, col
from app.models.user import User, UserCreate, UserUpdate
from app.core.security import get_password_hash


def get_user(session, user_id: int) -> Optional[User]:
    return session.get(User, user_id)


def get_user_by_email(session, email: str) -> Optional[User]:
    statement = select(User).where(User.email == email)
    return session.exec(statement).first()


def get_user_by_username(session, username: str) -> Optional[User]:
    statement = select(User).where(User.username == username)
    return session.exec(statement).first()


def find_users_by_username(
    session, username: str, skip: int = 0, limit: int = 100
) -> List[User]:
    statement = (
        select(User)
        .where(col(User.username).like(f"%{username}%"))
        .offset(skip)
        .limit(limit)
    )
    return session.exec(statement).all()


def find_users_by_fullname(
    session, fullname: str, skip: int = 0, limit: int = 100
) -> List[User]:
    statement = (
        select(User)
        .where(col(User.full_name).like(f"%{fullname}%"))
        .offset(skip)
        .limit(limit)
    )
    return session.exec(statement).all()


def get_users(session, skip: int = 0, limit: int = 100) -> List[User]:
    statement = select(User).offset(skip).limit(limit)
    return session.exec(statement).all()


def create_user(session, user_create: UserCreate) -> User:
    db_user = User(
        username=user_create.username,
        email=user_create.email,
        full_name=user_create.full_name,
        is_active=user_create.is_active,
        is_superuser=user_create.is_superuser,
        role=user_create.role,
        hashed_password=get_password_hash(user_create.password),
    )
    session.add(db_user)
    session.commit()
    session.refresh(db_user)
    return db_user


def update_user(session, user_id: int, user_update: UserUpdate) -> Optional[User]:
    db_user = session.get(User, user_id)
    if not db_user:
        return None

    # Update fields
    if user_update.username is not None:
        db_user.username = user_update.username
    if user_update.email is not None:
        db_user.email = user_update.email
    if user_update.full_name is not None:
        db_user.full_name = user_update.full_name
    if user_update.is_active is not None:
        db_user.is_active = user_update.is_active
    if user_update.is_superuser is not None:
        db_user.is_superuser = user_update.is_superuser
    if user_update.password is not None:
        db_user.hashed_password = get_password_hash(user_update.password)

    session.add(db_user)
    session.commit()
    session.refresh(db_user)
    return db_user


def update_user_profile(
    session, user_id: int, full_name: Optional[str]
) -> Optional[User]:
    """Update only the user's personal information (full_name)"""
    db_user = session.get(User, user_id)
    if not db_user:
        return None

    # Only update the full_name field
    if full_name is not None:
        db_user.full_name = full_name

    # Update the updated_at timestamp
    db_user.updated_at = datetime.utcnow()

    session.add(db_user)
    session.commit()
    session.refresh(db_user)
    return db_user


def delete_user(session, user_id: int) -> bool:
    db_user = session.get(User, user_id)
    if not db_user:
        return False
    session.delete(db_user)
    session.commit()
    return True
