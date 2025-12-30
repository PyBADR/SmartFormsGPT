# db.py - SmartFormsGPT Database Configuration

import os
from sqlalchemy import create_engine, MetaData
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
from logger import get_logger

# Load environment variables
load_dotenv()

logger = get_logger(__name__)

# Database URL from environment
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./smartforms.db")
DB_ECHO = os.getenv("DB_ECHO", "False").lower() == "true"

# Create engine
engine = create_engine(
    DATABASE_URL,
    echo=DB_ECHO,
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20
)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create base class for models
Base = declarative_base()
metadata = MetaData()

def get_db():
    """Dependency for getting database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():
    """Initialize database tables."""
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables created successfully")
    except Exception as e:
        logger.error(f"Error creating database tables: {e}")
        raise

# Export
__all__ = ["engine", "SessionLocal", "Base", "get_db", "init_db"]
