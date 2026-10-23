from fastapi import Depends, HTTPException, status
from fastapi.security import APIKeyCookie
from sqlalchemy.orm import Session

from .database import get_db
from .models import User
from .security import ACCESS_TOKEN_COOKIE, decode_access_token

# Reads the token from the HttpOnly cookie set at login; auto_error=False lets us answer 401 ourselves
cookie_scheme = APIKeyCookie(name=ACCESS_TOKEN_COOKIE, auto_error=False)

def get_current_user(
    token: str | None = Depends(cookie_scheme),
    db: Session = Depends(get_db),
) -> User:
    """FastAPI dependency: the logged-in user, or 401 if the cookie is missing or invalid."""
    unauthorized = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Not authenticated",
    )
    if token is None:
        raise unauthorized

    user_id = decode_access_token(token)
    if user_id is None:
        raise unauthorized

    user = db.get(User, user_id)
    if user is None:  # Token is valid but the account no longer exists
        raise unauthorized

    return user
