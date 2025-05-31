import uuid
import datetime
from sqlalchemy import Column, String, DateTime, Index
from backend.app.core.database import AuxBase

class CaptchaChallenge(AuxBase):
    __tablename__ = "captcha_challenges"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    question = Column(String(255), nullable=False)
    answer = Column(String(255), nullable=False) # Store answer as string
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    expires_at = Column(DateTime, nullable=False)

    __table_args__ = (
        Index('ix_captcha_challenges_expires_at', 'expires_at'),
    )

    def __repr__(self):
        return f"<CaptchaChallenge(id={self.id}, question='{self.question}', expires_at='{self.expires_at}')>"
