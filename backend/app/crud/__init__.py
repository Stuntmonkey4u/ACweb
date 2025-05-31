# This file makes the 'crud' directory a Python package.
# You can import CRUD functions here for convenience if desired.
# from .user import get_user_by_id, create_user

# Expose specific CRUD functions for easier access if you like
# For example, if you want to do `from backend.app.crud import user_crud`
# you could do:
# from . import user as user_crud

# Or directly expose functions:
from .user import get_user_by_username, create_user, authenticate_user, update_user_password, get_user_by_email, get_user_by_id
