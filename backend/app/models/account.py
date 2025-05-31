from sqlalchemy import Column, Integer, String, SmallInteger, Boolean, TIMESTAMP
from sqlalchemy.sql import func, expression # For server_default func.now() and expression.false()
from sqlalchemy.orm import Mapped, mapped_column

from backend.app.core.database import Base

class Account(Base):
    __tablename__ = "account"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    # AzerothCore typically stores username in uppercase. Application logic should handle this.
    username = Column(String(16), unique=True, index=True, nullable=False)
    sha_pass_hash = Column(String(40), nullable=False, default='') # SHA1 hash is 40 chars. AC default is empty string
    email = Column(String(255), unique=True, index=True, nullable=False)

    # Expansion: 0=Vanilla, 1=TBC, 2=WotLK. Default to WotLK (2).
    # AzerothCore uses 'tinyint unsigned'. SmallInteger is appropriate.
    expansion = Column(SmallInteger, nullable=False, default=2)

    reg_mail = Column(String(255), nullable=True, default='') # AC default is empty string
    last_ip = Column(String(15), nullable=False, default='0.0.0.0') # AC default

    # last_login: Handled by application logic or triggers in a full setup.
    # For simplicity, can be nullable or have a default.
    # Using server_default=func.now() for creation, onupdate=func.now() for updates.
    # However, onupdate is a DB-level feature that might need specific dialect handling.
    # For SQLAlchemy ORM, this is often handled at application level.
    # Let's use a simple default for creation time.
    joindate = Column(TIMESTAMP, nullable=False, server_default=func.now())
    last_login = Column(TIMESTAMP, nullable=True)

    locked = Column(Boolean, nullable=False, default=False)
    email_verified: Mapped[bool] = mapped_column(Boolean, default=False, server_default=expression.false())

    # Other common fields from AzerothCore 'account' table (optional, for reference or future use):
    # v = Column(String(255), nullable=False, default='')
    # s = Column(String(255), nullable=False, default='')
    # locale = Column(SmallInteger, nullable=False, default=0)
    # os = Column(String(3), nullable=False, default='')
    #recruiter = Column(Integer, nullable=False, default=0)
    #battlenet_account = Column(Integer, nullable=True, index=True) # or Integer if it's an ID
    #battlenet_index = Column(SmallInteger, nullable=True)
    #failed_logins = Column(Integer, nullable=False, default=0)
    #active_realm_id = Column(Integer, nullable=False, default=0)
    #token_auth = Column(String(100), nullable=True) # Used for remember me token

    def __repr__(self):
        return f"<Account(id={self.id}, username='{self.username}', email='{self.email}')>"
