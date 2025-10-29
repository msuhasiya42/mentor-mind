"""Database configuration and session management."""
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

# Database file path
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Get database URL from environment or fall back to SQLite for local development
# Vercel provides DATABASE_URL or POSTGRES_URL for Neon Postgres
DATABASE_URL = os.getenv("DATABASE_URL") or os.getenv("POSTGRES_URL") or f"sqlite:///{os.path.join(BASE_DIR, 'mentor_mind.db')}"

# Handle postgres:// vs postgresql:// URL scheme (Heroku/Neon compatibility)
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

# Create engine with appropriate configuration for Postgres or SQLite
if DATABASE_URL.startswith("postgresql://"):
    # PostgreSQL configuration
    engine = create_engine(
        DATABASE_URL,
        pool_pre_ping=True,  # Verify connections before using them
        pool_size=5,         # Connection pool size
        max_overflow=10,     # Max overflow connections
        echo=False           # Set to True for SQL query debugging
    )
else:
    # SQLite configuration (local development)
    engine = create_engine(
        DATABASE_URL,
        connect_args={"check_same_thread": False},  # Needed for SQLite
        echo=False  # Set to True for SQL query debugging
    )

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for models
Base = declarative_base()


def get_db():
    """Dependency to get database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """Initialize database - create all tables."""
    from .models import LearningPath, UserAction
    Base.metadata.create_all(bind=engine)
    print("✅ Database initialized successfully!")
