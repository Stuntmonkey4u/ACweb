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

# Auxiliary SQLite database
AUX_SQLALCHEMY_DATABASE_URL = f"sqlite:///./{settings.AUX_DB_NAME}"
aux_engine = create_engine(AUX_SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
AuxSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=aux_engine)
AuxBase = declarative_base()

# Dependency to get DB session in FastAPI routes
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Dependency to get auxiliary DB session in FastAPI routes
def get_aux_db():
    db = AuxSessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():
    # Import all modules here that might define models so that
    # they will be registered properly on the metadata. Otherwise
    # you will have to import them first before calling init_db()
    # from ..models import Account # Example, ensure your models are imported
    from ..models.email_verification_token import EmailVerificationToken # Ensure this is created
    Base.metadata.create_all(bind=engine)
    logger.info("Main database tables created (if they didn't exist).")

def init_aux_db():
    # Import all models that use AuxBase so they are registered
    from ..models.user_totp import UserTOTP
    from ..models.captcha_challenge import CaptchaChallenge
    AuxBase.metadata.create_all(bind=aux_engine)
    logger.info("Auxiliary database tables created (if they didn't exist).")

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
