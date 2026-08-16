from typing import Generator
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker, Session
from app.config import settings

db_url = settings.database_uri

# Configure engine kwargs based on DB driver
connect_args = {}
if db_url.startswith("sqlite"):
    connect_args["check_same_thread"] = False

engine = create_engine(
    db_url,
    connect_args=connect_args,
    pool_pre_ping=True,  # Test connections before using them (vital for RDS/ALB health checks)
    echo=False
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db() -> Generator[Session, None, None]:
    """
    FastAPI dependency that provides a transactional database session per request.
    Automatically closes the session when request completes.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
