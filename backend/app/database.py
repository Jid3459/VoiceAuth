from sqlalchemy import create_engine, event
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import QueuePool
from .config import get_settings
from .logger import get_logger

logger = get_logger(__name__)
settings = get_settings()

# Enhanced engine with connection pooling
engine = create_engine(
    settings.DATABASE_URL,
    # SQLite-specific settings
    connect_args={"check_same_thread": False} if "sqlite" in settings.DATABASE_URL else {},
    
    # Connection pooling (for production databases)
    poolclass=QueuePool,
    pool_size=10,  # Number of connections to maintain
    max_overflow=20,  # Max additional connections when pool is full
    pool_pre_ping=True,  # Test connections before using
    pool_recycle=3600,  # Recycle connections after 1 hour
    
    echo=False  # Set to True for SQL query logging
)

# Enable SQLite optimizations
@event.listens_for(engine, "connect")
def set_sqlite_pragma(dbapi_conn, connection_record):
    """Set SQLite performance optimizations"""
    if "sqlite" in settings.DATABASE_URL:
        cursor = dbapi_conn.cursor()
        # WAL mode for better concurrency
        cursor.execute("PRAGMA journal_mode=WAL")
        # Faster synchronization
        cursor.execute("PRAGMA synchronous=NORMAL")
        # Larger cache
        cursor.execute("PRAGMA cache_size=10000")
        # Foreign key support
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()
        logger.debug("SQLite optimizations applied")

SessionLocal = sessionmaker(
    autocommit=False, 
    autoflush=False, 
    bind=engine,
    expire_on_commit=False  # Prevent lazy loading errors
)

Base = declarative_base()

def get_db():
    """Dependency for getting database session"""
    db = SessionLocal()
    try:
        yield db
    except Exception as e:
        logger.error(f"Database session error: {e}")
        db.rollback()
        raise
    finally:
        db.close()

def init_db():
    """Initialize database - create all tables"""
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Database initialization error: {e}")
        raise