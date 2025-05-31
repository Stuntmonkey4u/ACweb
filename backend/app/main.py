from fastapi import FastAPI
from backend.app.api.endpoints import auth as auth_router # auth.py is in endpoints directory
from backend.app.core.config import settings
from backend.app.core.database import engine, Base # Import engine and Base for table creation
# from backend.app.models import account as account_model # Import your SQLAlchemy models
# No, we need to import all models that use Base so they are registered with metadata
from backend.app.models import account # This ensures Account model is registered
from backend.app.models import user # This ensures User Pydantic models are available if needed by FastAPI for other things, though not strictly for table creation.


import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create database tables if they don't exist
# This is a simple way for development. For production, you'd use Alembic migrations.
try:
    Base.metadata.create_all(bind=engine)
    logger.info("Database tables created or verified successfully (if they already exist).")
except Exception as e:
    logger.error(f"Error creating database tables: {e}")
    # Depending on the severity, you might want to exit or handle this
    # For now, just log it. The app might still run if tables exist.


app = FastAPI(
    title="AzerothCore Account Management API",
    description="API for managing AzerothCore user accounts, with LAN-first focus.",
    version="0.1.0"
)

logger.info(f"API Settings Loaded. DB Host: {settings.DB_HOST}, DB Name: {settings.DB_NAME}")

app.include_router(auth_router.router, prefix="/api/auth", tags=["Authentication"])

@app.get("/api/health")
async def health_check():
    # TODO: Add a DB check here if possible by trying to make a simple query
    # For now, this just confirms the API is running.
    # Example DB check:
    # try:
    #     db = next(get_db()) # Get a DB session
    #     db.execute("SELECT 1")
    #     db_status = "healthy"
    # except Exception as e:
    #     logger.error(f"Health check DB connection failed: {e}")
    #     db_status = "unhealthy"
    # finally:
    #     if 'db' in locals() and db is not None:
    #         db.close()
    # return {"status": "healthy", "database_status": db_status, "message": "Welcome to AzerothCore Account Management API"}
    return {"status": "healthy", "message": "Welcome to AzerothCore Account Management API"}


@app.get("/")
async def root_redirect_to_docs():
    from fastapi.responses import RedirectResponse
    return RedirectResponse(url="/docs")
