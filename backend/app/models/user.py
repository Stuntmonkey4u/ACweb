from pydantic import BaseModel, EmailStr, constr
from typing import Optional

class UserBase(BaseModel):
    username: constr(min_length=3, max_length=16, regex="^[a-zA-Z0-9_]+$")
    email: EmailStr
    email_verified: bool = False
    # is_admin: bool = False # Removed
    locked: bool = False
    gmlevel: int = 0 # Default to 0 for Pydantic model instances

class UserCreate(UserBase):
    password: constr(min_length=6, max_length=100)
    captcha_id: str
    captcha_solution: str

class UserUpdate(UserBase): # For updating user info
    email: Optional[EmailStr] = None
    # Add other updatable fields here, e.g. is_active, etc. but not password

class UserInDBBase(UserBase):
    id: int
    email_verified: bool
    # is_admin: bool # Removed
    locked: bool
    gmlevel: int # Will get value from ORM model
    # expansion: int # Example, if you want to return it
    # Add other fields from 'account' table you want to expose

    class Config:
        orm_mode = True # Important for SQLAlchemy model conversion

class User(UserInDBBase): # Full user model for responses
    pass

class UserInDB(UserInDBBase): # Representation of user in DB, might include hashed_password
    sha_pass_hash: str


class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None

class PasswordChange(BaseModel):
    current_password: str
    new_password: constr(min_length=6, max_length=100)
