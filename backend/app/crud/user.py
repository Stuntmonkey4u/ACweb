from sqlalchemy.orm import Session
from backend.app.models import account as account_model # SQLAlchemy model
from backend.app.models import user as user_schema # Pydantic schemas
from backend.app.services.auth import get_ac_password_hash, verify_ac_password
import logging

logger = logging.getLogger(__name__)

def get_user_by_id(db: Session, user_id: int) -> account_model.Account | None:
    return db.query(account_model.Account).filter(account_model.Account.id == user_id).first()

def get_user_by_username(db: Session, username: str) -> account_model.Account | None:
    # AC account usernames are case-insensitive in practice, but stored typically uppercase.
    # For lookup, it's safer to compare with the same case as stored or use case-insensitive query if DB supports.
    # Here, assuming username is passed as is, and DB collation handles case-insensitivity or it's stored as passed.
    return db.query(account_model.Account).filter(account_model.Account.username == username).first()

def get_user_by_email(db: Session, email: str) -> account_model.Account | None:
    return db.query(account_model.Account).filter(account_model.Account.email == email).first()

def create_user(db: Session, user: user_schema.UserCreate) -> account_model.Account:
    hashed_password = get_ac_password_hash(password=user.password, username=user.username)
    # Default expansion is set in the model itself (2 for WotLK)
    # Username should ideally be stored in uppercase as per AC standards.
    db_user = account_model.Account(
        username=user.username.upper(), # Store username in uppercase
        email=user.email,
        sha_pass_hash=hashed_password,
        reg_mail=user.email # Assuming reg_mail is the same as email initially
        # joindate will be handled by DB default (func.now())
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    logger.info(f"User {db_user.username} created successfully with ID {db_user.id}")
    return db_user

def update_user_password(db: Session, user: account_model.Account, new_password_plain: str) -> account_model.Account:
    new_hashed_password = get_ac_password_hash(password=new_password_plain, username=user.username)
    user.sha_pass_hash = new_hashed_password
    db.commit()
    db.refresh(user)
    logger.info(f"Password updated for user {user.username}")
    return user

# Add other update functions as needed, e.g., for email, expansion, lock status
# def update_user_email(db: Session, user: account_model.Account, new_email: str) -> account_model.Account:
#     user.email = new_email
#     # Potentially update reg_mail as well if that's the policy
#     # user.reg_mail = new_email
#     db.commit()
#     db.refresh(user)
#     logger.info(f"Email updated for user {user.username}")
#     return user

# Placeholder for authenticating user (might be slightly different from pure CRUD)
def authenticate_user(db: Session, username: str, password_plain: str) -> account_model.Account | None:
    # Assuming username for login attempt can be mixed case, but it's stored uppercase.
    db_user = get_user_by_username(db, username=username.upper())
    if not db_user:
        logger.warning(f"Authentication failed: User {username.upper()} not found.")
        return None
    if not verify_ac_password(plain_password=password_plain, username=db_user.username, hashed_password_from_db=db_user.sha_pass_hash):
        logger.warning(f"Authentication failed: Incorrect password for user {db_user.username}.")
        return None
    logger.info(f"User {db_user.username} authenticated successfully.")
    return db_user

def mark_user_email_as_verified(db: Session, user_id: int) -> account_model.Account | None:
    db_user = get_user_by_id(db, user_id)
    if db_user:
        db_user.email_verified = True
        db.commit()
        db.refresh(db_user)
        logger.info(f"Email marked as verified for user ID {user_id}")
        return db_user
    logger.warning(f"Attempted to mark email as verified for non-existent user ID {user_id}")
    return None

# --- Admin CRUD Functions ---

def get_all_users(db: Session) -> list[account_model.Account]:
    return db.query(account_model.Account).all()

def ban_account(db: Session, user: account_model.Account) -> account_model.Account:
    user.locked = True # In AC, 1 typically means locked/banned
    db.commit()
    db.refresh(user)
    logger.info(f"Account {user.username} (ID: {user.id}) has been banned.")
    return user

def unban_account(db: Session, user: account_model.Account) -> account_model.Account:
    user.locked = False # In AC, 0 typically means not locked/banned
    db.commit()
    db.refresh(user)
    logger.info(f"Account {user.username} (ID: {user.id}) has been unbanned.")
    return user

def promote_to_admin(db: Session, user: account_model.Account) -> account_model.Account:
    user.is_admin = True
    db.commit()
    db.refresh(user)
    logger.info(f"Account {user.username} (ID: {user.id}) has been promoted to admin.")
    return user

def demote_from_admin(db: Session, user: account_model.Account) -> account_model.Account:
    user.is_admin = False
    db.commit()
    db.refresh(user)
    logger.info(f"Account {user.username} (ID: {user.id}) has been demoted from admin.")
    return user
