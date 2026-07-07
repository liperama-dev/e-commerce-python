from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.config import settings

router = APIRouter(prefix="/api/auth", tags=["auth"])


class LoginRequest(BaseModel):
    username: str
    password: str


class LoginResponse(BaseModel):
    token: str
    message: str = "Login successful"


class HintResponse(BaseModel):
    username: str
    password: str


@router.post("/login", response_model=LoginResponse)
def login(request: LoginRequest):
    """
    Authenticate with username and password.
    Returns the admin token to be sent as X-Admin-Key on protected requests.
    """
    if (
        request.username != settings.admin_username
        or request.password != settings.admin_password
    ):
        raise HTTPException(status_code=401, detail="Invalid username or password")

    return LoginResponse(token=settings.admin_secret_key)


@router.get("/hint", response_model=HintResponse)
def get_credentials_hint():
    """
    Returns the default admin credentials.
    Only available when TESTING=true — useful for reviewers running locally.
    Returns 404 in production.
    """
    if not settings.testing:
        raise HTTPException(status_code=404, detail="Not found")

    return HintResponse(
        username=settings.admin_username,
        password=settings.admin_password,
    )
