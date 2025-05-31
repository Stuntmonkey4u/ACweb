from fastapi import APIRouter, Depends, Request
from pydantic import BaseModel
from typing import Optional

from backend.app.core.config import settings # Direct import of settings
from backend.app.models.account import Account as AccountModel
from backend.app.api.dependencies import get_current_active_user # Assuming this is the correct path
from backend.app.core.rate_limiter import limiter

router = APIRouter(
    prefix="/api/downloads",
    tags=["Downloads"]
)

class ClientDownloadInfo(BaseModel):
    lan_available: bool
    lan_download_url: Optional[str]
    public_download_url: Optional[str]

def is_lan_ip(ip_address: str) -> bool:
    """
    Placeholder function to check if an IP address is within a typical LAN range.
    This is a very basic check and might need to be more robust based on specific network setups.
    Common private IP ranges: 10.0.0.0/8, 172.16.0.0/12, 192.168.0.0/16.
    Also includes localhost.
    """
    if ip_address == "127.0.0.1" or ip_address == "::1":
        return True
    if ip_address.startswith("192.168."):
        return True
    if ip_address.startswith("10."):
        return True
    if ip_address.startswith("172."):
        parts = ip_address.split('.')
        if len(parts) >= 2:
            try:
                second_octet = int(parts[1])
                if 16 <= second_octet <= 31:
                    return True
            except ValueError:
                return False # Not a valid IP part
    return False

@router.get("/client-info", response_model=ClientDownloadInfo)
@limiter.limit(settings.RATE_LIMIT_DEFAULT) # Apply rate limiting
async def get_client_download_info(
    request: Request,
    current_user: AccountModel = Depends(get_current_active_user) # Require authentication
):
    client_ip = request.client.host if request.client else None
    lan_available_flag = False

    if client_ip and settings.LAN_DOWNLOAD_URL:
        if is_lan_ip(client_ip):
            lan_available_flag = True

    # If LAN URL is not configured, lan_available should be false regardless of IP
    if not settings.LAN_DOWNLOAD_URL:
        lan_available_flag = False

    return ClientDownloadInfo(
        lan_available=lan_available_flag,
        lan_download_url=settings.LAN_DOWNLOAD_URL if lan_available_flag else None, # Only show LAN URL if available
        public_download_url=settings.PUBLIC_DOWNLOAD_URL
    )
