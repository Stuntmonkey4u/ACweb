from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordBearer # OAuth2PasswordRequestForm removed as login uses custom model
from sqlalchemy.orm import Session
from typing import Optional
import random

from backend.app.core.database import get_db, get_aux_db
from backend.app.models import user as user_schema
from backend.app.models import account as account_model # SQLAlchemy model
from backend.app.crud import user as user_crud
from backend.app.crud import email_verification as email_verification_crud
from backend.app.crud import user_totp as user_totp_crud
from backend.app.crud import captcha as captcha_crud # Added
from backend.app.services import auth as auth_service
from backend.app.services import email_service
from backend.app.services import totp_service
from backend.app.services import captcha_service
from backend.app.core.config import settings
from backend.app.core.rate_limiter import limiter # Import the limiter
import logging

router = APIRouter()
logger = logging.getLogger(__name__)

# Note: If RATE_LIMIT_ENABLED is False, the limiter's default ("10000/second")
# will effectively disable throttling for these endpoints.
# An alternative would be to conditionally apply decorators, but that's more complex.

# tokenUrl should point to the actual login endpoint that provides the token
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login/token")


@router.post("/register", response_model=user_schema.User)
@limiter.limit(settings.RATE_LIMIT_REGISTER)
async def register_user( # Changed to async
    request: Request, # Added for limiter
    user_data: user_schema.UserCreate,
    db: Session = Depends(get_db),
    aux_db: Session = Depends(get_aux_db)
):
    logger.info(f"Registration attempt for username: {user_data.username} with CAPTCHA ID {user_data.captcha_id}")

    # CAPTCHA Validation
    challenge = captcha_crud.get_challenge(aux_db, user_data.captcha_id)
    if not challenge:
        logger.warning(f"Registration CAPTCHA failed for {user_data.username}: Invalid or expired CAPTCHA ID {user_data.captcha_id}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid or expired CAPTCHA. Please try again.")

    if challenge.answer.lower() != user_data.captcha_solution.lower():
        logger.warning(f"Registration CAPTCHA failed for {user_data.username}: Incorrect solution for CAPTCHA ID {user_data.captcha_id}")
        # Delete the used (incorrect) challenge to prevent brute-forcing the same challenge
        captcha_crud.delete_challenge(aux_db, user_data.captcha_id)
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Incorrect CAPTCHA solution.")

    # Valid CAPTCHA, delete it
    captcha_crud.delete_challenge(aux_db, user_data.captcha_id)
    logger.info(f"CAPTCHA validation successful for {user_data.username}, ID {user_data.captcha_id}")

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

        if settings.SMTP_HOST and settings.SMTP_SENDER_EMAIL:
            verification_token = email_verification_crud.create_verification_token(db=db, user_id=created_user.id)
            if verification_token:
                email_sent = email_service.send_verification_email(
                    user_email=created_user.email,
                    username=created_user.username,
                    verification_token=verification_token.token
                )
                if email_sent:
                    logger.info(f"Verification email initiated for {created_user.username} to {created_user.email}.")
                else:
                    logger.warning(f"Failed to send verification email for {created_user.username} to {created_user.email} (SMTP issue or offline).")
            else:
                logger.error(f"Failed to create verification token for user {created_user.username}")
        else:
            logger.info("SMTP not configured. Skipping verification email for new user.")
            # If SMTP is not configured, you might want to auto-verify or handle differently.
            # For now, email_verified will remain False unless explicitly verified.

        # Pydantic model 'User' has orm_mode = True, so it will convert from SQLAlchemy model
        return created_user
    except Exception as e:
        logger.error(f"Error during user creation or email sending for {user_data.username}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred during registration."
        )

@router.post("/login/token", response_model=user_schema.Token)
@limiter.limit(settings.RATE_LIMIT_LOGIN)
async def login_for_access_token( # Changed to async
    request: Request, # Added for limiter
    form_data: LoginForm, # Use custom Pydantic model (already was)
    db: Session = Depends(get_db),
    aux_db: Session = Depends(get_aux_db)
):
    logger.info(f"Login attempt for username: {form_data.username}")
    user = user_crud.authenticate_user(db, username=form_data.username, password_plain=form_data.password)

    if not user:
        logger.warning(f"Login failed for {form_data.username}: Invalid username or password.")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # 2FA Check (already implemented)
    user_totp_settings = user_totp_crud.get_user_totp_secret(aux_db, user.id)
    if user_totp_settings and user_totp_settings.is_active:
        logger.info(f"2FA is active for user {user.username}. Verifying TOTP code.")
        if not form_data.totp_code:
            logger.warning(f"Login failed for {user.username}: TOTP code required but not provided.")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="TOTP code required."
            )

        if not totp_service.verify_totp_code(user_totp_settings.secret_key, form_data.totp_code):
            logger.warning(f"Login failed for {user.username}: Invalid TOTP code provided.")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid TOTP code."
            )
        logger.info(f"TOTP code verified for user {user.username}.")
    elif user_totp_settings and not user_totp_settings.is_active:
        logger.info(f"2FA is not fully active for user {user.username}. Proceeding without TOTP check.")
    else:
        logger.info(f"2FA is not configured for user {user.username}. Proceeding without TOTP check.")

    access_token = auth_service.create_access_token(data={"sub": user.username})
    logger.info(f"User {user.username} logged in successfully.")
    return {"access_token": access_token, "token_type": "bearer"}


# Pydantic model for Login
class LoginForm(user_schema.BaseModel):
    username: str
    password: str
    totp_code: Optional[str] = None

# Pydantic models for 2FA endpoints
class TOTPSetupResponse(user_schema.BaseModel):
    secret_key: str # Only show once during setup
    otp_uri: str
    qr_code_data_uri: str

class TOTPEnableRequest(user_schema.BaseModel):
    totp_code: str

class TOTPDisableRequest(user_schema.BaseModel):
    totp_code: str


# Dependency to get current user from token (no rate limit here, applied on endpoints using it)
async def get_current_active_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> account_model.Account : # Changed to async
    # This function itself doesn't need `request: Request` unless it's directly limited,
    # which is not common for a dependency like this.
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
@limiter.limit(settings.RATE_LIMIT_DEFAULT) # Example: Apply default limit
async def read_users_me(
    request: Request, # Added
    current_user: account_model.Account = Depends(get_current_active_user)
): # Changed to async
    logger.info(f"User {current_user.username} accessed /users/me endpoint.")
    return current_user

@router.post("/users/me/change-password", response_model=user_schema.User)
@limiter.limit(settings.RATE_LIMIT_DEFAULT) # Example: Apply default limit
async def change_current_user_password( # Changed to async
    request: Request, # Added
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
    new_password: user_schema.constr(min_length=6, max_length=100) # Added user_schema
    username: str # To identify the user, though token should ideally be the primary identifier

class PasswordResetRequestPayload(user_schema.BaseModel):
    username: str # Or email, depending on policy
    captcha_id: str
    captcha_solution: str

@router.post("/password-reset/request")
@limiter.limit(settings.RATE_LIMIT_PASSWORD_RESET)
async def request_password_reset( # Already async
    request: Request, # Added
    payload: PasswordResetRequestPayload,
    db: Session = Depends(get_db),
    aux_db: Session = Depends(get_aux_db)
):
    logger.info(f"Password reset request for username: {payload.username} with CAPTCHA ID {payload.captcha_id}")

    # CAPTCHA Validation
    challenge = captcha_crud.get_challenge(aux_db, payload.captcha_id)
    if not challenge:
        logger.warning(f"Password reset CAPTCHA failed for {payload.username}: Invalid or expired CAPTCHA ID {payload.captcha_id}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid or expired CAPTCHA. Please try again.")

    if challenge.answer.lower() != payload.captcha_solution.lower():
        logger.warning(f"Password reset CAPTCHA failed for {payload.username}: Incorrect solution for CAPTCHA ID {payload.captcha_id}")
        captcha_crud.delete_challenge(aux_db, payload.captcha_id) # Delete used challenge
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Incorrect CAPTCHA solution.")

    captcha_crud.delete_challenge(aux_db, payload.captcha_id) # Delete valid challenge
    logger.info(f"CAPTCHA validation successful for password reset for {payload.username}, ID {payload.captcha_id}")

    user = user_crud.get_user_by_username(db, username=payload.username.upper())
    if not user:
        # Even if user not found, don't reveal that. Standard practice.
        logger.info(f"Password reset requested for non-existent or provided username: {payload.username.upper()}")
    else:
        # TODO: Implement actual password reset token generation and email sending here
        # For now, this is a placeholder as per original logic
        logger.info(f"Password reset requested and CAPTCHA verified for user {user.username}. Token generation/handling TBD (offline).")

    # Consistent message regardless of user existence to prevent enumeration
    return {"message": "If a user with that username exists and CAPTCHA is valid, a password reset process would be initiated. (Offline handling TBD)"}


class EmailVerifyRequest(user_schema.BaseModel):
    token: str

@router.post("/verify-email")
@limiter.limit(settings.RATE_LIMIT_VERIFY_EMAIL_CONFIRM)
async def verify_email( # Changed to async
    request: Request, # Added
    verification_data: EmailVerifyRequest,
    db: Session = Depends(get_db)
):
    logger.info(f"Email verification attempt with token: {verification_data.token[:10]}...")

    db_token = email_verification_crud.get_verification_token(db, token=verification_data.token)

    if not db_token:
        logger.warning(f"Email verification failed: Invalid or expired token provided.")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired verification token."
        )

    user = user_crud.mark_user_email_as_verified(db, user_id=db_token.user_id)
    if not user:
        # This case should ideally not happen if token is valid and user_id exists
        logger.error(f"Email verification failed: User with ID {db_token.user_id} not found after token validation.")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, # Or 400, as token might be for a deleted user
            detail="User not found for this token."
        )

    email_verification_crud.delete_verification_token(db, token_id=db_token.id)
    logger.info(f"Email successfully verified for user ID {db_token.user_id} (Username: {user.username}). Token deleted.")

    return {"message": "Email verified successfully."}


@router.post("/password-reset/confirm")
@limiter.limit(settings.RATE_LIMIT_PASSWORD_RESET) # Same as request, or could be different
async def confirm_password_reset( # Already async
    request: Request, # Added
    reset_data: PasswordResetConfirm,
    db: Session = Depends(get_db)
):
    logger.info(f"Password reset confirmation attempt for user {reset_data.username.upper()} with token {reset_data.token}")

    # Username from payload should be uppercased for lookup, consistent with storage
    user = user_crud.get_user_by_username(db, username=reset_data.username.upper())
    if not user:
        # This check might be slightly different if token itself contains user identifier securely
        logger.warning(f"Password reset failed: User {reset_data.username.upper()} not found for token confirmation.")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid user or token.")

    # Simulate token check (very basic, replace with real logic using a secure token service)
    # In a real system, thẻ token itself should be the primary key for lookup, not username + token.
    # The token would be associated with a user_id and have an expiry.
    if reset_data.token == "mock_valid_token_for_" + user.username: # user.username is already uppercase
        user_crud.update_user_password(db, user, reset_data.new_password)
        logger.info(f"Password reset for {user.username} successful via mock token.")
        return {"message": "Password has been reset successfully."}
    else:
        logger.warning(f"Password reset for {user.username} failed: Invalid mock token provided: {reset_data.token}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid or expired reset token.")

# --- 2FA Endpoints ---

@router.post("/2fa/setup", response_model=TOTPSetupResponse)
@limiter.limit(settings.RATE_LIMIT_2FA_SETUP)
async def setup_2fa( # Changed to async
    request: Request, # Added
    current_user: account_model.Account = Depends(get_current_active_user),
    aux_db: Session = Depends(get_aux_db)
):
    logger.info(f"2FA setup initiated for user {current_user.username}")

    # Check if 2FA is already active
    existing_totp = user_totp_crud.get_user_totp_secret(aux_db, current_user.id)
    if existing_totp and existing_totp.is_active:
        logger.warning(f"2FA setup attempt for {current_user.username} but 2FA is already active.")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="2FA is already active for this account.")

    secret = totp_service.generate_totp_secret()
    # Store the secret (inactive) in the auxiliary database
    user_totp_crud.create_user_totp_secret(db=aux_db, user_id=current_user.id, secret_key=secret)

    # Use user's email for the OTP URI if available and verified, otherwise username.
    # AC username is uppercase.
    otp_account_name = current_user.email if current_user.email_verified else current_user.username
    otp_uri = totp_service.get_totp_uri(secret, otp_account_name, issuer_name=settings.APP_NAME if hasattr(settings, 'APP_NAME') else "AzerothCoreMgr")
    qr_code_uri = totp_service.generate_qr_code_data_uri(otp_uri)

    logger.info(f"2FA secret generated for {current_user.username}. QR code and URI provided.")
    return {
        "secret_key": secret, # Important: Remind user to save this securely
        "otp_uri": otp_uri,
        "qr_code_data_uri": qr_code_uri
    }

@router.post("/2fa/enable")
@limiter.limit(settings.RATE_LIMIT_2FA_ENABLE_DISABLE)
async def enable_2fa( # Changed to async
    request: Request, # Added
    totp_data: TOTPEnableRequest,
    current_user: account_model.Account = Depends(get_current_active_user),
    aux_db: Session = Depends(get_aux_db)
):
    logger.info(f"2FA enable attempt for user {current_user.username}")
    user_totp = user_totp_crud.get_user_totp_secret(aux_db, current_user.id)

    if not user_totp or not user_totp.secret_key:
        logger.warning(f"2FA enable failed for {current_user.username}: No secret found. Setup required first.")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="2FA setup not initiated or secret key missing.")

    if user_totp.is_active:
        logger.info(f"2FA enable attempt for {current_user.username}, but 2FA is already active.")
        return {"message": "2FA is already active."}

    if totp_service.verify_totp_code(user_totp.secret_key, totp_data.totp_code):
        user_totp_crud.activate_user_totp(aux_db, current_user.id)
        logger.info(f"2FA successfully enabled for user {current_user.username}.")
        return {"message": "2FA has been successfully enabled."}
    else:
        logger.warning(f"2FA enable failed for {current_user.username}: Invalid TOTP code.")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid TOTP code.")


# --- CAPTCHA Endpoints ---
class CaptchaChallengeResponse(user_schema.BaseModel):
    id: str
    question: str

@router.get("/captcha/generate", response_model=CaptchaChallengeResponse)
@limiter.limit(settings.RATE_LIMIT_CAPTCHA_GENERATE)
async def generate_captcha_challenge( # Changed to async
    request: Request, # Added
    aux_db: Session = Depends(get_aux_db)
):
    # Periodically clean up expired challenges (simple strategy)
    if random.random() < 0.1: # 10% chance to run cleanup
        # Note: DB operations in async context. FastAPI handles sync calls in threadpool.
        # If this were a pure async ORM, await would be needed for DB calls.
        deleted_count = captcha_crud.delete_expired_challenges(aux_db)
        if deleted_count > 0:
            logger.info(f"Cleaned up {deleted_count} expired CAPTCHA challenges.")

    question, answer = captcha_service.generate_math_challenge()
    challenge = captcha_crud.create_challenge(
        db=aux_db,
        question=question,
        answer=answer,
        expires_in_seconds=captcha_service.CAPTCHA_EXPIRY_SECONDS
    )
    return CaptchaChallengeResponse(id=challenge.id, question=challenge.question)

@router.post("/2fa/disable")
@limiter.limit(settings.RATE_LIMIT_2FA_ENABLE_DISABLE)
async def disable_2fa( # Changed to async
    request: Request, # Added
    totp_data: TOTPDisableRequest,
    current_user: account_model.Account = Depends(get_current_active_user),
    aux_db: Session = Depends(get_aux_db)
):
    logger.info(f"2FA disable attempt for user {current_user.username}")
    user_totp = user_totp_crud.get_user_totp_secret(aux_db, current_user.id)

    if not user_totp or not user_totp.is_active:
        logger.warning(f"2FA disable failed for {current_user.username}: 2FA is not active.")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="2FA is not currently active.")

    if totp_service.verify_totp_code(user_totp.secret_key, totp_data.totp_code):
        user_totp_crud.deactivate_user_totp(aux_db, current_user.id) # Or delete, depending on CRUD implementation
        logger.info(f"2FA successfully disabled for user {current_user.username}.")
        return {"message": "2FA has been successfully disabled."}
    else:
        logger.warning(f"2FA disable failed for {current_user.username}: Invalid TOTP code.")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid TOTP code.")
