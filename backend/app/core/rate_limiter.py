from slowapi import Limiter
from slowapi.util import get_remote_address
from backend.app.core.config import settings
import logging
import redis # Import for explicit check

logger = logging.getLogger(__name__)

def get_storage_uri():
    if settings.RATE_LIMIT_ENABLED and settings.REDIS_HOST and settings.REDIS_PORT:
        try:
            # Test Redis connection
            r = redis.Redis(
                host=settings.REDIS_HOST,
                port=settings.REDIS_PORT,
                socket_connect_timeout=1, # Short timeout for check
                socket_timeout=1 # Short timeout for commands
            )
            r.ping()
            logger.info(f"Rate limiter using Redis at: redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}")
            return f"redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}"
        except redis.exceptions.ConnectionError as e:
            logger.warning(f"Redis configured for rate limiter, but connection failed: {e}. Falling back to in-memory storage.")
            return "memory://"
        except Exception as e: # Catch other potential errors like redis not installed if not explicitly checked
            logger.warning(f"An unexpected error occurred while connecting to Redis for rate limiter: {e}. Falling back to in-memory storage.")
            return "memory://"

    logger.info("Rate limiter using in-memory storage (Redis not configured or rate limiting disabled).")
    return "memory://"

limiter_storage_uri = get_storage_uri()

# Determine default limits based on whether rate limiting is enabled
if settings.RATE_LIMIT_ENABLED:
    default_limits_list = [settings.RATE_LIMIT_DEFAULT]
else:
    # Effectively disable by providing a very high limit or specific "unlimited" string if supported
    # "inf/minute" is not a standard format; use a very high number or rely on disabling elsewhere.
    # For slowapi, not passing default_limits or an empty list might mean no default global limit.
    # Or, more explicitly, if RATE_LIMIT_ENABLED is false, we can skip applying decorators.
    # For now, let's assume if it's disabled, we'll handle it by not applying limits or using a high limit.
    # A common way is to have a very high limit like "10000/second" or simply not apply the limiter.
    # Given the structure, we'll set a high limit here if disabled.
    default_limits_list = ["10000/second"]


limiter = Limiter(
    key_func=get_remote_address,
    default_limits=default_limits_list,
    storage_uri=limiter_storage_uri,
    strategy="moving-window",  # Recommended for fairness
    # auto_check=True # auto_check is True by default
)
