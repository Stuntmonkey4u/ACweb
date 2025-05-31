from sqlalchemy.orm import Session
from backend.app.models.user_totp import UserTOTP # SQLAlchemy model for UserTOTP
import datetime

# Note: This CRUD module will use get_aux_db for sessions,
# which needs to be passed in when these functions are called from endpoints.

def create_user_totp_secret(db: Session, user_id: int, secret_key: str) -> UserTOTP:
    """
    Creates or updates a user's TOTP secret. If a secret already exists,
    it updates the secret_key and resets is_active to False,
    forcing re-verification.
    """
    existing_totp = db.query(UserTOTP).filter(UserTOTP.user_id == user_id).first()
    if existing_totp:
        existing_totp.secret_key = secret_key
        existing_totp.is_active = False
        existing_totp.updated_at = datetime.datetime.utcnow()
        db_totp = existing_totp
    else:
        db_totp = UserTOTP(
            user_id=user_id,
            secret_key=secret_key,
            is_active=False
        )
        db.add(db_totp)
    db.commit()
    db.refresh(db_totp)
    return db_totp

def get_user_totp_secret(db: Session, user_id: int) -> UserTOTP | None:
    """
    Retrieves a user's TOTP secret, regardless of its active status.
    """
    return db.query(UserTOTP).filter(UserTOTP.user_id == user_id).first()

def activate_user_totp(db: Session, user_id: int) -> UserTOTP | None:
    """
    Marks a user's TOTP secret as active.
    Returns the updated UserTOTP object or None if not found.
    """
    db_totp = db.query(UserTOTP).filter(UserTOTP.user_id == user_id).first()
    if db_totp:
        db_totp.is_active = True
        db_totp.updated_at = datetime.datetime.utcnow()
        db.commit()
        db.refresh(db_totp)
        return db_totp
    return None

def deactivate_user_totp(db: Session, user_id: int) -> UserTOTP | None:
    """
    Marks a user's TOTP secret as inactive.
    Alternatively, this could delete the record. For now, just deactivating.
    Returns the updated UserTOTP object or None if not found.
    """
    db_totp = db.query(UserTOTP).filter(UserTOTP.user_id == user_id).first()
    if db_totp:
        db_totp.is_active = False
        # Optionally, clear the secret_key or delete the record for enhanced security upon deactivation.
        # For now, keeping the secret but marking inactive.
        # db_totp.secret_key = "" # Example if clearing
        db_totp.updated_at = datetime.datetime.utcnow()
        db.commit()
        db.refresh(db_totp)
        return db_totp
    # If you prefer to delete:
    # if db_totp:
    #     db.delete(db_totp)
    #     db.commit()
    #     return db_totp # Or return True/None indicating deletion status
    return None
