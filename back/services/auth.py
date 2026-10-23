from sqlalchemy import select
from sqlalchemy.orm import Session

from ..models import User
from ..security import DUMMY_HASH, hash_password, needs_rehash, verify_password

def authenticate_user(db: Session, username_or_email: str, password: str) -> User | None:
    """Return the user if the credentials are correct, None otherwise."""
    if "@" in username_or_email:
        query = select(User).where(User.email == username_or_email.lower())
    else:
        query = select(User).where(User.username == username_or_email)
    user = db.scalars(query).first()

    if user is None:
        verify_password(password, DUMMY_HASH)  # Same work as a real check, so timing doesn't reveal it
        return None

    if not verify_password(password, user.hashed_password):
        return None

    if needs_rehash(user.hashed_password):
        user.hashed_password = hash_password(password)
        db.commit()

    return user
