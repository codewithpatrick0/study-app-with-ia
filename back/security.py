from argon2 import PasswordHasher
from argon2.exceptions import InvalidHashError, VerificationError

# Argon2id with the library's recommended defaults (memory-hard, salted per hash)
password_hasher = PasswordHasher()

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
