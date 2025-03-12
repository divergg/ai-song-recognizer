from fastapi import HTTPException, status, Request
from src.configs import settings


def verify_token(request: Request = None, header_token: str = None):
    token = None
    if request:
        token = request.headers.get("Authorization")
    if header_token:
        token = header_token
    if not token or token != f"Bearer {settings.app.token}":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid authentication token"
        )
    return True
