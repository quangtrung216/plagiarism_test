from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
from typing import Optional
from app.database.session import get_session
from app.core.auth import authenticate_user, create_user_access_token
from app.schemas.token import (
    Token,
    LoginRequest,
)
from app.core.user_service import get_user_by_email, get_user_by_username, create_user
from app.models.user import UserCreate, UserRole, Student, Teacher

router = APIRouter()


@router.post("/login", response_model=Token)
def login(login_request: LoginRequest, session: Session = Depends(get_session)):
    user = authenticate_user(session, login_request.username, login_request.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Thông tin tài khoản không đúng",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_user_access_token(user)
    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/register", status_code=status.HTTP_201_CREATED)
def register(
    user_create: UserCreate,
    class_or_department: Optional[str] = None,
    session: Session = Depends(get_session),
):
    # Validate required fields
    if not user_create.username:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Vui lòng nhập mã",
        )

    if not user_create.email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Vui lòng nhập email",
        )

    if not user_create.password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Vui lòng nhập mật khẩu",
        )

    if not class_or_department:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Vui lòng nhập đủ thông tin",
        )

    # Check if user already exists by username
    existing_user = get_user_by_username(session, user_create.username)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Người dùng với mã này đã tồn tại",
        )

    # Also check if email already exists
    existing_user = get_user_by_email(session, user_create.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Người dùng với email này đã tồn tại",
        )

    # For students, check if student_id (username) already exists
    if user_create.role == UserRole.STUDENT:
        statement = select(Student).where(Student.student_id == user_create.username)
        existing_student = session.exec(statement).first()
        if existing_student:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Người dùng với mã này đã tồn tại",
            )

    # For teachers, check if employee_id (username) already exists
    if user_create.role == UserRole.TEACHER and user_create.username:
        statement = select(Teacher).where(Teacher.employee_id == user_create.username)
        existing_teacher = session.exec(statement).first()
        if existing_teacher:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Người dùng với mã này đã tồn tại",
            )

    # Create new user
    new_user = create_user(session, user_create)

    # Create role-specific profile
    if user_create.role == UserRole.STUDENT and class_or_department:
        # Ensure the user ID is available
        assert new_user.id is not None, "User ID should be available after creation"
        student_profile = Student(
            user_id=new_user.id,
            student_id=user_create.username,  # Use username as student ID
            major=class_or_department,
        )
        session.add(student_profile)
        session.commit()
    elif user_create.role == UserRole.TEACHER and class_or_department:
        # Ensure the user ID is available
        assert new_user.id is not None, "User ID should be available after creation"
        teacher_profile = Teacher(
            user_id=new_user.id,
            employee_id=user_create.username,  # Use username as employee ID
            department=class_or_department,
        )
        session.add(teacher_profile)
        session.commit()

    return {"message": "Đăng ký thành công", "user_id": new_user.id}
