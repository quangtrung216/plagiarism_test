from sqlmodel import create_engine, Session
from app.core.config import settings

# Create engine with connection pooling settings appropriate for Docker
engine = create_engine(
    settings.DATABASE_URL, echo=True, pool_pre_ping=True, pool_recycle=300
)


def get_session():
    with Session(engine) as session:
        yield session
