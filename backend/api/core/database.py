"""
AI SaaS Platform - Database Module
Database connection and models setup
"""

from sqlalchemy import create_engine, MetaData
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from typing import Generator
import logging

from .config import settings

logger = logging.getLogger(__name__)

# Database URL
if settings.database_url:
    DATABASE_URL = settings.database_url
else:
    DATABASE_URL = f"postgresql://{settings.postgres_user}:{settings.postgres_password}@{settings.postgres_server}/{settings.postgres_db}"

# Create SQLAlchemy engine
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    pool_recycle=300,
    echo=settings.debug
)

# Session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for models
Base = declarative_base()
metadata = MetaData()

def get_db() -> Generator[Session, None, None]:
    """
    Database dependency for FastAPI
    
    Usage:
        def get_users(db: Session = Depends(get_db)):
            return db.query(User).all()
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def create_tables():
    """Create all database tables"""
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("✅ Database tables created successfully")
    except Exception as e:
        logger.error(f"❌ Failed to create tables: {e}")
        raise

def init_db():
    """Initialize database connection"""
    try:
        # Test connection
        with engine.connect() as conn:
            conn.execute("SELECT 1")
        logger.info("✅ Database connection established")
        return True
    except Exception as e:
        logger.error(f"❌ Database connection failed: {e}")
        return False

# Export
__all__ = [
    "engine",
    "SessionLocal",
    "Base",
    "get_db",
    "create_tables",
    "init_db",
    "metadata",
]

print("✅ Database module loaded")
