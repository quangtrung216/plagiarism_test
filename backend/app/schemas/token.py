from typing import Optional
from sqlmodel import SQLModel


class Token(SQLModel):
    access_token: str
    token_type: str


class TokenData(SQLModel):
    username: Optional[str] = None


class LoginRequest(SQLModel):
    username: str
    password: str


class PasswordResetRequest(SQLModel):
    email: str


class PasswordResetConfirm(SQLModel):
    token: str
    new_password: str
