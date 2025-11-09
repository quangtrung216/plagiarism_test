import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from sqlmodel import SQLModel
from app.core.config import settings
from sqlalchemy import create_engine
from sqlmodel import Session
from app.database.session import engine
from app.models.user import User, UserRole
from app.models.permission import Role
from app.core.permission_service import PermissionService
from app.core.security import get_password_hash


def init_db():
    """Initialize database tables and seed initial data"""
    # First create the database if it doesn't exist
    try:
        db_engine = create_database_if_not_exists()
        # Create all tables
        SQLModel.metadata.create_all(bind=db_engine)
    except Exception as e:
        print(f"Error creating database or tables: {e}")
        # If database creation fails, try with existing engine
        SQLModel.metadata.create_all(bind=engine)

    # Initialize permissions and roles
    try:
        with Session(engine) as session:
            permission_service = PermissionService(session)
            permission_service.initialize_system_permissions()

            # Seed initial data
            seed_initial_data(session)
    except Exception as e:
        print(f"Error initializing permissions or seeding data: {e}")


def reset_db():
    """Reset the database by dropping all tables and recreating them"""
    # First create the database if it doesn't exist
    try:
        db_engine = create_database_if_not_exists()
        # Drop all tables
        SQLModel.metadata.drop_all(bind=db_engine)
        # Create all tables
        SQLModel.metadata.create_all(bind=db_engine)
        print("Database tables dropped and recreated successfully!")
    except Exception as e:
        print(f"Error resetting database: {e}")
        # If database creation fails, try with existing engine
        SQLModel.metadata.drop_all(bind=engine)
        SQLModel.metadata.create_all(bind=engine)

    # Initialize permissions and roles
    try:
        with Session(engine) as session:
            permission_service = PermissionService(session)
            permission_service.initialize_system_permissions()

            # Seed initial data
            seed_initial_data(session)
    except Exception as e:
        print(f"Error initializing permissions or seeding data: {e}")


def seed_initial_data(session: Session):
    """Seed the database with initial data"""
    try:
        # Check if users already exist
        from sqlmodel import select

        existing_users = session.exec(select(User)).first()

        if not existing_users:
            # Create default admin user
            admin_user = User(
                username="admin",
                email="admin@example.com",
                full_name="System Administrator",
                role=UserRole.ADMIN,
                hashed_password=get_password_hash("admin123"),
                is_superuser=True,
                is_active=True,
            )
            session.add(admin_user)
            session.commit()
            session.refresh(admin_user)

            # Create default teacher user
            teacher_user = User(
                username="teacher",
                email="teacher@example.com",
                full_name="Default Teacher",
                role=UserRole.TEACHER,
                hashed_password=get_password_hash("teacher123"),
                is_superuser=False,
                is_active=True,
            )
            session.add(teacher_user)
            session.commit()
            session.refresh(teacher_user)

            # Create default student user
            student_user = User(
                username="student",
                email="student@example.com",
                full_name="Default Student",
                role=UserRole.STUDENT,
                hashed_password=get_password_hash("student123"),
                is_superuser=False,
                is_active=True,
            )
            session.add(student_user)
            session.commit()
            session.refresh(student_user)

            # Assign roles to users using the permission service
            admin_role = session.exec(select(Role).where(Role.name == "admin")).first()
            teacher_role = session.exec(
                select(Role).where(Role.name == "teacher")
            ).first()
            student_role = session.exec(
                select(Role).where(Role.name == "student")
            ).first()

            if admin_role and teacher_role and student_role:
                # Assign roles to users
                from app.models.permission import UserRoleAssignment
                from datetime import datetime

                # Assign admin role to admin user
                admin_assignment = UserRoleAssignment(
                    user_id=admin_user.id,  # type: ignore
                    role_id=admin_role.id,  # type: ignore
                    granted_by=admin_user.id,  # type: ignore
                    granted_at=datetime.utcnow(),
                    is_active=True,
                )
                session.add(admin_assignment)

                # Assign teacher role to teacher user
                teacher_assignment = UserRoleAssignment(
                    user_id=teacher_user.id,  # type: ignore
                    role_id=teacher_role.id,  # type: ignore
                    granted_by=admin_user.id,  # type: ignore
                    granted_at=datetime.utcnow(),
                    is_active=True,
                )
                session.add(teacher_assignment)

                # Assign student role to student user
                student_assignment = UserRoleAssignment(
                    user_id=student_user.id,  # type: ignore
                    role_id=student_role.id,  # type: ignore
                    granted_by=admin_user.id,  # type: ignore
                    granted_at=datetime.utcnow(),
                    is_active=True,
                )
                session.add(student_assignment)

                session.commit()

            print("Seeded initial users:")
            print("Admin: admin / admin123")
            print("Teacher: teacher / teacher123")
            print("Student: student / student123")
        else:
            print("Database already seeded with initial data.")
    except Exception as e:
        session.rollback()
        print(f"Error seeding initial data: {e}")


def create_database_if_not_exists():
    # Parse the DATABASE_URL to get connection details
    # Format: postgresql://username:password@localhost:5432/plagiarism_detection
    import re

    match = re.match(
        r"postgresql://([^:]+):([^@]+)@([^:]+):(\d+)/(.+)", settings.DATABASE_URL
    )
    if not match:
        raise ValueError("Invalid DATABASE_URL format")

    username, password, host, port, dbname = match.groups()

    # Connect to PostgreSQL server (without specifying database)
    conn = psycopg2.connect(host=host, port=port, user=username, password=password)
    conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    cursor = conn.cursor()

    # Check if database exists
    cursor.execute("SELECT 1 FROM pg_catalog.pg_database WHERE datname = %s", (dbname,))
    exists = cursor.fetchone()

    # Create database if it doesn't exist
    if not exists:
        cursor.execute(f'CREATE DATABASE "{dbname}"')
        print(f"Database '{dbname}' created successfully!")
    else:
        print(f"Database '{dbname}' already exists.")

    cursor.close()
    conn.close()

    # Now create an engine specifically for the newly created database
    # This ensures we can connect to the database for table creation
    db_engine = create_engine(settings.DATABASE_URL, echo=True)
    return db_engine


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "reset":
        reset_db()
        print("Database reset successfully!")
    else:
        init_db()
        print("Database initialized successfully!")
