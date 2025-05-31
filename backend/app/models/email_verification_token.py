from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from backend.app.core.database import Base

class EmailVerificationToken(Base):
    __tablename__ = "email_verification_token"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("account.id"))
    token = Column(String(128), unique=True, index=True)
    expires_at = Column(DateTime)
