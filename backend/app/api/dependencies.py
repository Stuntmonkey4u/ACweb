from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session # Needed for DB session in get_current_active_user
from backend.app.core.database import get_db # Needed for DB session
from backend.app.models.account import Account as AccountModel
from backend.app.models import user as user_schema # For TokenData
from backend.app.services import auth as auth_service # For verify_token
from backend.app.crud import user as user_crud # For get_user_by_username
from backend.app.api.endpoints.auth import oauth2_scheme # oauth2_scheme also needed, or move it too

# Consider moving oauth2_scheme here if it's broadly used, or pass as arg if preferred.
# For now, keeping it simple by direct import, assuming auth.py is loaded.

async def get_current_active_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> AccountModel:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        token_data = auth_service.verify_token(token, credentials_exception)
        if token_data.username is None: # username is the 'sub'
             raise credentials_exception
    except Exception: # Includes JWTError from verify_token
        raise credentials_exception

    user = user_crud.get_user_by_username(db, username=token_data.username)
    if user is None:
        raise credentials_exception
    if user.locked:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Account locked.")
    # Could add check for user.is_active here if such a field existed
    return user

async def get_current_admin_user(current_user: AccountModel = Depends(get_current_active_user)) -> AccountModel:
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="The user doesn't have enough privileges." # Corrected typo
        )
    return current_user
