import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from sqlmodel import SQLModel
from app.core.config import settings
from app.database.session import engine


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


def init_db():
    # First create the database if it doesn't exist
    create_database_if_not_exists()

    # Then create all tables
    SQLModel.metadata.create_all(engine)


if __name__ == "__main__":
    init_db()
    print("Database initialized successfully!")
