from fastapi import Header, HTTPException

from app.config import settings


def verify_admin_key(x_admin_key: str = Header(None)) -> str:
    """Dependency to enforce X-Admin-Key authentication."""
    if not x_admin_key or x_admin_key != settings.admin_secret_key:
        raise HTTPException(
            status_code=401, detail="Invalid or missing X-Admin-Key header"
        )
    return x_admin_key
