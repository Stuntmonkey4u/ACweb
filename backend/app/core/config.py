from pydantic import BaseSettings

class Settings(BaseSettings):
    DB_HOST: str = "localhost"
    DB_USER: str = "acore"
    DB_PASSWORD: str = "acore"
    DB_NAME: str = "ac_auth"
    DB_PORT: int = 3306

    SECRET_KEY: str = "your_super_secret_key_please_change_this"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24

    AUX_DB_NAME: str = "app_data.sqlite"
    APP_NAME: str = "AzerothCore Manager" # Used for TOTP issuer name

    # SMTP Settings for email verification
    SMTP_HOST: str | None = None
    SMTP_PORT: int | None = 587
    SMTP_USER: str | None = None
    SMTP_PASSWORD: str | None = None
    SMTP_SENDER_EMAIL: str | None = None # Should be EmailStr but EmailStr is not available here
    EMAIL_VERIFICATION_URL_LIFESPAN_SECONDS: int = 3600
    FRONTEND_URL: str = "http://localhost:3000"

    # Redis and Rate Limiting
    REDIS_HOST: str | None = None
    REDIS_PORT: int = 6379
    RATE_LIMIT_ENABLED: bool = True
    RATE_LIMIT_DEFAULT: str = "100/minute" # Default general limit, increased from 5
    RATE_LIMIT_LOGIN: str = "20/minute" # Increased from 10
    RATE_LIMIT_REGISTER: str = "10/hour" # Increased from 5
    RATE_LIMIT_PASSWORD_RESET: str = "10/hour" # Increased from 5
    # RATE_LIMIT_VERIFY_EMAIL_REQUEST: str = "5/hour" # No such endpoint currently
    RATE_LIMIT_VERIFY_EMAIL_CONFIRM: str = "20/minute" # For /verify-email endpoint
    RATE_LIMIT_2FA_SETUP: str = "10/hour"
    RATE_LIMIT_2FA_ENABLE_DISABLE: str = "10/minute" # For enable/disable 2FA attempts
    RATE_LIMIT_CAPTCHA_GENERATE: str = "60/minute"

    # Client Download URLs
    LAN_DOWNLOAD_URL: str | None = "http://192.168.1.100/downloads/wow_client.zip" # Example LAN URL
    PUBLIC_DOWNLOAD_URL: str | None = "https://download.example.com/wow_client.zip" # Example Public URL


    class Config:
        env_file = ".env"

settings = Settings()
