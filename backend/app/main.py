from fastapi import FastAPI
from backend.app.api.endpoints import auth as auth_router # auth.py is in endpoints directory
from backend.app.core.config import settings
from backend.app.core.database import engine, Base # Import engine and Base for table creation
# from backend.app.models import account as account_model # Import your SQLAlchemy models
# No, we need to import all models that use Base so they are registered with metadata
from backend.app.models import account # This ensures Account model is registered
from backend.app.models import user # This ensures User Pydantic models are available if needed by FastAPI for other things, though not strictly for table creation.


import logging
from backend.app.core.database import init_db, init_aux_db
from backend.app.core.rate_limiter import limiter # Import the limiter instance
from slowapi.errors import RateLimitExceeded # Import the exception
from slowapi import _rate_limit_exceeded_handler # Import the default handler

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="AzerothCore Account Management API",
    description="API for managing AzerothCore user accounts, with LAN-first focus. Rate limiting active.",
    version="0.1.0"
)

# Add limiter state and exception handler to the app
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

@app.on_event("startup")
async def startup_event():
    logger.info("Starting up application and initializing databases...")
    try:
        init_db() # Initialize main database tables
        init_aux_db() # Initialize auxiliary database tables
        logger.info("Databases initialized successfully.")
    except Exception as e:
        logger.error(f"Error initializing databases: {e}")
        # Optionally, re-raise the exception or exit if DB initialization is critical
        # raise e

logger.info(f"API Settings Loaded. DB Host: {settings.DB_HOST}, DB Name: {settings.DB_NAME}")

from backend.app.api.endpoints import admin as admin_router
from backend.app.api.endpoints import downloads as downloads_router # Import downloads router
app.include_router(auth_router.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(admin_router.router) # Prefix and tags are defined in admin.py
app.include_router(downloads_router.router) # Prefix and tags are defined in downloads.py

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
