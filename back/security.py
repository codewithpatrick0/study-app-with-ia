from datetime import datetime, timedelta, timezone

import jwt
from argon2 import PasswordHasher
from argon2.exceptions import InvalidHashError, VerificationError

from .config.settings import settings

JWT_ALGORITHM = "HS256"
ACCESS_TOKEN_COOKIE = "access_token"

# Argon2id with the library's recommended defaults (memory-hard, salted per hash)
password_hasher = PasswordHasher()

# Checked when the user doesn't exist, so a failed login takes the same time either way
DUMMY_HASH = password_hasher.hash("dummy-password-for-timing")

def hash_password(password: str) -> str:
    """Return an Argon2 hash; the salt and parameters are stored inside it."""
    return password_hasher.hash(password)

def verify_password(password: str, hashed_password: str) -> bool:
    """True if the password matches the stored hash, False otherwise."""
    try:
        return password_hasher.verify(hashed_password, password)
    except (VerificationError, InvalidHashError):
        return False

def needs_rehash(hashed_password: str) -> bool:
    """True if the hash was made with older parameters and should be updated."""
    return password_hasher.check_needs_rehash(hashed_password)

def create_access_token(user_id: int) -> str:
    """Signed JWT that identifies the user until it expires."""
    now = datetime.now(timezone.utc)
    payload = {
        "sub": str(user_id),  # Subject: who the token belongs to
        "iat": now,           # Issued at
        "exp": now + timedelta(minutes=settings.access_token_expire_minutes),
    }
    return jwt.encode(payload, settings.jwt_secret_key, algorithm=JWT_ALGORITHM)

def decode_access_token(token: str) -> int | None:
    """Return the user id inside a valid token, or None if it's forged, expired or malformed."""
    try:
        payload = jwt.decode(
            token,
            settings.jwt_secret_key,
            algorithms=[JWT_ALGORITHM],  # Only accept the algorithm we sign with
            options={"require": ["sub", "iat", "exp"]},
        )
        return int(payload["sub"])
    except (jwt.InvalidTokenError, ValueError):
        return None
