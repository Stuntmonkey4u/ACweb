from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from backend.app.core.database import get_db # For DB session dependency
from backend.app.models import user as user_schema
from backend.app.models import account as account_model # SQLAlchemy model
from backend.app.crud import user as user_crud
from backend.app.services import auth as auth_service
from backend.app.core.config import settings # For JWT settings, if needed directly here
import logging

router = APIRouter()
logger = logging.getLogger(__name__)

# tokenUrl should point to the actual login endpoint that provides the token
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login/token")

@router.post("/register", response_model=user_schema.User)
def register_user(user_data: user_schema.UserCreate, db: Session = Depends(get_db)):
    logger.info(f"Registration attempt for username: {user_data.username}")
    # Usernames in AC are typically case-insensitive but stored as entered or uppercase.
    # The CRUD operations should handle querying consistently (e.g. by converting input to uppercase for lookup)

    db_user_by_username = user_crud.get_user_by_username(db, username=user_data.username.upper()) # Ensure consistent case for check
    if db_user_by_username:
        logger.warning(f"Registration failed: Username {user_data.username.upper()} already exists.")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered"
        )

    db_user_by_email = user_crud.get_user_by_email(db, email=user_data.email)
    if db_user_by_email:
        logger.warning(f"Registration failed: Email {user_data.email} already registered.")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

    try:
        # CRUD create_user now stores username in uppercase
        created_user = user_crud.create_user(db=db, user=user_data)
        logger.info(f"User {created_user.username} successfully registered with ID {created_user.id}")
        # Pydantic model 'User' has orm_mode = True, so it will convert from SQLAlchemy model
        return created_user
    except Exception as e:
        logger.error(f"Error during user creation for {user_data.username}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred during registration."
        )

@router.post("/login/token", response_model=user_schema.Token)
def login_for_access_token(db: Session = Depends(get_db), form_data: OAuth2PasswordRequestForm = Depends()):
    logger.info(f"Login attempt for username: {form_data.username}")
    # crud.authenticate_user handles username casing (compares with uppercase stored username)
    user = user_crud.authenticate_user(db, username=form_data.username, password_plain=form_data.password)
    if not user:
        logger.warning(f"Login failed for {form_data.username}: Invalid credentials.")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # TODO: Add 2FA check here if enabled for the user (Phase 3)

    access_token = auth_service.create_access_token(data={"sub": user.username}) # Use actual username from DB user object
    logger.info(f"User {user.username} logged in successfully.")
    return {"access_token": access_token, "token_type": "bearer"}

# Dependency to get current user from token
def get_current_active_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> account_model.Account :
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        token_data = auth_service.verify_token(token, credentials_exception)
        if token_data.username is None:
             raise credentials_exception
    except Exception:
        raise credentials_exception

    # Username from token (subject) should be uppercase as it's stored
    user = user_crud.get_user_by_username(db, username=token_data.username)
    if user is None:
        logger.warning(f"Token validation failed: User {token_data.username} not found.")
        raise credentials_exception

    if user.locked:
        logger.warning(f"Authentication failed for {user.username}: Account is locked.")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Account locked.")

    return user

@router.get("/users/me", response_model=user_schema.User)
def read_users_me(current_user: account_model.Account = Depends(get_current_active_user)):
    logger.info(f"User {current_user.username} accessed /users/me endpoint.")
    return current_user

@router.post("/users/me/change-password", response_model=user_schema.User)
def change_current_user_password(
    password_data: user_schema.PasswordChange,
    current_user: account_model.Account = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    logger.info(f"Password change attempt for user: {current_user.username}")
    if not auth_service.verify_ac_password(
        plain_password=password_data.current_password,
        username=current_user.username, # verify_ac_password will handle casing
        hashed_password_from_db=current_user.sha_pass_hash
    ):
        logger.warning(f"Password change failed for {current_user.username}: Incorrect current password.")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Incorrect current password.")

    user_crud.update_user_password(db=db, user=current_user, new_password_plain=password_data.new_password)
    logger.info(f"Password successfully changed for user: {current_user.username}")
    return current_user

class PasswordResetConfirm(user_schema.BaseModel): # Defined here as it's specific to this endpoint's payload
    token: str
    new_password: constr(min_length=6, max_length=100)
    username: str # To identify the user, though token should ideally be the primary identifier

@router.post("/password-reset/request")
async def request_password_reset(username: str, db: Session = Depends(get_db)):
    user = user_crud.get_user_by_username(db, username=username.upper()) # Check against uppercase
    if not user:
        # Even if user not found, don't reveal that. Standard practice.
        logger.info(f"Password reset requested for non-existent or provided username: {username.upper()}")
    else:
        logger.info(f"Password reset requested for user {user.username}. Token generation/handling TBD (offline).")
    # In a real scenario: generate token, store it, inform user (e.g., via admin).
    return {"message": "If a user with that username exists, a password reset process would be initiated. (Offline handling TBD)"}


@router.post("/password-reset/confirm")
async def confirm_password_reset(reset_data: PasswordResetConfirm, db: Session = Depends(get_db)):
    logger.info(f"Password reset confirmation attempt for user {reset_data.username.upper()} with token {reset_data.token}")

    # Username from payload should be uppercased for lookup, consistent with storage
    user = user_crud.get_user_by_username(db, username=reset_data.username.upper())
    if not user:
        # This check might be slightly different if token itself contains user identifier securely
        logger.warning(f"Password reset failed: User {reset_data.username.upper()} not found for token confirmation.")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid user or token.")

    # Simulate token check (very basic, replace with real logic using a secure token service)
    # In a real system, the token itself should be the primary key for lookup, not username + token.
    # The token would be associated with a user_id and have an expiry.
    if reset_data.token == "mock_valid_token_for_" + user.username: # user.username is already uppercase
        user_crud.update_user_password(db, user, reset_data.new_password)
        logger.info(f"Password reset for {user.username} successful via mock token.")
        return {"message": "Password has been reset successfully."}
    else:
        logger.warning(f"Password reset for {user.username} failed: Invalid mock token provided: {reset_data.token}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid or expired reset token.")
