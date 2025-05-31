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

    class Config:
        env_file = ".env"

settings = Settings()
