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
    import logging
    logger = logging.getLogger(__name__)

    try:
        # Import models to register them with Base
        from .models import LearningPath, UserAction

        logger.info(f"Creating tables in database: {DATABASE_URL[:50]}...")

        # Create all tables
        Base.metadata.create_all(bind=engine)

        # Verify tables were created
        inspector = None
        try:
            from sqlalchemy import inspect
            inspector = inspect(engine)
            tables = inspector.get_table_names()
            logger.info(f"✅ Database tables created: {tables}")
        except Exception as inspect_error:
            logger.warning(f"Could not verify tables: {inspect_error}")

        print("✅ Database initialized successfully!")
        return True

    except Exception as e:
        logger.error(f"Failed to initialize database: {str(e)}", exc_info=True)
        raise
