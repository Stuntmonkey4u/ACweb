import datetime
from sqlalchemy.orm import Session
from backend.app.models.captcha_challenge import CaptchaChallenge

def create_challenge(db: Session, question: str, answer: str, expires_in_seconds: int) -> CaptchaChallenge:
    expires_at = datetime.datetime.utcnow() + datetime.timedelta(seconds=expires_in_seconds)
    db_challenge = CaptchaChallenge(
        question=question,
        answer=answer,
        expires_at=expires_at
    )
    db.add(db_challenge)
    db.commit()
    db.refresh(db_challenge)
    return db_challenge

def get_challenge(db: Session, challenge_id: str) -> CaptchaChallenge | None:
    challenge = db.query(CaptchaChallenge).filter(CaptchaChallenge.id == challenge_id).first()
    if challenge:
        # Optional: Check for expiry here and delete if expired, then return None
        if challenge.expires_at < datetime.datetime.utcnow():
            delete_challenge(db, challenge_id=challenge.id)
            return None
        return challenge
    return None

def delete_challenge(db: Session, challenge_id: str) -> bool:
    challenge = db.query(CaptchaChallenge).filter(CaptchaChallenge.id == challenge_id).first()
    if challenge:
        db.delete(challenge)
        db.commit()
        return True
    return False

def delete_expired_challenges(db: Session) -> int:
    """Deletes all expired CAPTCHA challenges and returns the count of deleted items."""
    now = datetime.datetime.utcnow()
    expired_count = db.query(CaptchaChallenge).filter(CaptchaChallenge.expires_at < now).delete()
    db.commit()
    return expired_count
