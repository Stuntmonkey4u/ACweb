import hashlib
from datetime import datetime, timedelta, timezone
from jose import JWTError, jwt
from backend.app.core.config import settings
from backend.app.models.user import TokenData # Assuming TokenData is in user.py
from typing import Optional

# For AzerothCore's specific SHA1 hash: SHA1(UPPER(USERNAME) + ':' + UPPER(PASSWORD))
def verify_ac_password(plain_password: str, username: str, hashed_password_from_db: str) -> bool:
    salt_and_pass = f"{username.upper()}:{plain_password.upper()}"
    recalculated_hash = hashlib.sha1(salt_and_pass.encode('utf-8')).hexdigest()
    return recalculated_hash.lower() == hashed_password_from_db.lower()

def get_ac_password_hash(password: str, username: str) -> str:
    salt_and_pass = f"{username.upper()}:{password.upper()}"
    return hashlib.sha1(salt_and_pass.encode('utf-8')).hexdigest()

# JWT Handling
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt

def verify_token(token: str, credentials_exception) -> TokenData:
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        username: Optional[str] = payload.get("sub")
        if username is None:
            raise credentials_exception
        return TokenData(username=username)
    except JWTError:
        raise credentials_exception
