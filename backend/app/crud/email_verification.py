import secrets
import datetime
from sqlalchemy.orm import Session
from backend.app.models.email_verification_token import EmailVerificationToken
from backend.app.core.config import settings

def create_verification_token(db: Session, user_id: int) -> EmailVerificationToken:
    token = secrets.token_urlsafe(32)
    expires_at = datetime.datetime.utcnow() + datetime.timedelta(seconds=settings.EMAIL_VERIFICATION_URL_LIFESPAN_SECONDS)
    db_token = EmailVerificationToken(
        user_id=user_id,
        token=token,
        expires_at=expires_at
    )
    db.add(db_token)
    db.commit()
    db.refresh(db_token)
    return db_token

def get_verification_token(db: Session, token: str) -> EmailVerificationToken | None:
    db_token = db.query(EmailVerificationToken).filter(EmailVerificationToken.token == token).first()
    if db_token and db_token.expires_at > datetime.datetime.utcnow():
        return db_token
    # Also delete expired tokens
    if db_token and db_token.expires_at <= datetime.datetime.utcnow():
        delete_verification_token(db, db_token.id)
    return None

def delete_verification_token(db: Session, token_id: int) -> None:
    db_token = db.query(EmailVerificationToken).filter(EmailVerificationToken.id == token_id).first()
    if db_token:
        db.delete(db_token)
        db.commit()
