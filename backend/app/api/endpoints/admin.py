from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from typing import List

from backend.app.core.database import get_db
from backend.app.models import user as user_schema
from backend.app.models.account import Account as AccountModel
from backend.app.crud import user as user_crud
from backend.app.api.dependencies import get_current_admin_user # Import the actual dependency
from backend.app.core.rate_limiter import limiter
from backend.app.core.config import settings

router = APIRouter(
    prefix="/api/admin",
    tags=["Admin"],
    dependencies=[Depends(get_current_admin_user)] # Apply admin check to all routes in this router
)

@router.get("/users", response_model=List[user_schema.User])
@limiter.limit(settings.RATE_LIMIT_DEFAULT) # Apply a general admin rate limit
async def list_users(
    request: Request,
    db: Session = Depends(get_db),
    # admin_user: AccountModel = Depends(get_current_admin_user) # Already applied at router level
):
    users = user_crud.get_all_users(db)
    return users

@router.post("/users/{user_id}/ban", response_model=user_schema.User)
@limiter.limit(settings.RATE_LIMIT_DEFAULT)
async def ban_user_endpoint( # Renamed to avoid conflict with crud function if imported directly
    request: Request,
    user_id: int,
    db: Session = Depends(get_db),
    admin_user: AccountModel = Depends(get_current_admin_user) # Explicitly get admin for self-action checks
):
    target_user = user_crud.get_user_by_id(db, user_id=user_id)
    if not target_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    if target_user.id == admin_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admins cannot ban themselves.")
    # Check against gmlevel; assuming admin_user (current user) is already verified as admin (gmlevel >= 3)
    if target_user.gmlevel >= 3: # Prevent banning other admins (gmlevel 3+)
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Cannot ban other admin users.")

    banned_user = user_crud.ban_account(db, target_user)
    return banned_user

@router.post("/users/{user_id}/unban", response_model=user_schema.User)
@limiter.limit(settings.RATE_LIMIT_DEFAULT)
async def unban_user_endpoint( # Renamed
    request: Request,
    user_id: int,
    db: Session = Depends(get_db),
    # admin_user: AccountModel = Depends(get_current_admin_user) # Not strictly needed if not checking self-action
):
    target_user = user_crud.get_user_by_id(db, user_id=user_id)
    if not target_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    # No special checks for unbanning (e.g. unbanning another admin is fine)
    unbanned_user = user_crud.unban_account(db, target_user)
    return unbanned_user

# Promote and Demote endpoints are removed as per requirements.
# @router.post("/users/{user_id}/promote", response_model=user_schema.User)
# @limiter.limit(settings.RATE_LIMIT_DEFAULT)
# async def promote_user_endpoint( ... )

# @router.post("/users/{user_id}/demote", response_model=user_schema.User)
# @limiter.limit(settings.RATE_LIMIT_DEFAULT)
# async def demote_user_endpoint( ... )
