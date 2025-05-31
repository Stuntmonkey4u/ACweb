from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from .config import settings
import logging

logger = logging.getLogger(__name__)

SQLALCHEMY_DATABASE_URL = f"mysql+mysqlclient://{settings.DB_USER}:{settings.DB_PASSWORD}@{settings.DB_HOST}:{settings.DB_PORT}/{settings.DB_NAME}"

try:
    engine = create_engine(SQLALCHEMY_DATABASE_URL)
    # Test connection
    with engine.connect() as connection:
        logger.info(f"Successfully created SQLAlchemy engine for MySQL database: {settings.DB_NAME}")
except Exception as e:
    logger.error(f"Error creating SQLAlchemy engine for MySQL: {e}")
    # Fallback or exit strategy if engine creation fails
    # For now, we'll let it raise or be None if not handled elsewhere
    engine = None

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# Optional: a dependency to get DB session in FastAPI routes
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

if __name__ == "__main__":
    # This is for testing purposes if the file is run directly
    logger.info(f"Attempting to connect with SQLAlchemy to {SQLALCHEMY_DATABASE_URL}")
    if engine:
        try:
            # Test connection by creating a session
            db = SessionLocal()
            db.execute("SELECT 1") # Simple query to test connection
            logger.info("SQLAlchemy test connection successful and query executed.")
            db.close()
        except Exception as e:
            logger.error(f"SQLAlchemy test connection or query failed: {e}")
    else:
        logger.error("SQLAlchemy engine is not initialized.")
