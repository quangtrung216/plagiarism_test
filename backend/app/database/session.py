from sqlmodel import create_engine, Session
from app.core.config import settings

# Create engine with connection pooling settings appropriate for Docker
# Note: This engine will only work if the database already exists
# For initial database creation, use the init_db.py script
engine = None
try:
    engine = create_engine(
        settings.DATABASE_URL, echo=False, pool_pre_ping=True, pool_recycle=300
    )
except Exception as e:
    # Engine creation may fail if database doesn't exist yet
    # This is expected during initial setup
    print(f"Warning: Could not create engine. Database may not exist yet: {e}")


def get_session():
    if engine is None:
        raise Exception(
            "Database engine is not available. Please run init_db.py first."
        )
    with Session(engine) as session:
        yield session
