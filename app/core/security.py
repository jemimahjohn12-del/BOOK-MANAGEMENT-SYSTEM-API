from datetime import datetime, timedelta, timezone

import bcrypt
import jwt

from app.core import config


def hash_password(password: str) -> str:
    hashed = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())
    return hashed.decode("utf-8")


def verify_password(password: str, password_hash: str) -> bool:
    try:
        return bcrypt.checkpw(password.encode("utf-8"), password_hash.encode("utf-8"))
    except ValueError:
        return False


def create_access_token(user_id: int) -> str:
    if not config.JWT_SECRET:
        raise RuntimeError("JWT_SECRET is not set")
    expires = datetime.now(timezone.utc) + timedelta(
        minutes=config.ACCESS_TOKEN_EXPIRE_MINUTES
    )
    payload = {"sub": str(user_id), "exp": expires}
    return jwt.encode(payload, config.JWT_SECRET, algorithm=config.JWT_ALGORITHM)


def decode_access_token(token: str) -> dict:
    # Raises an error if the token is fake, changed, or expired
    return jwt.decode(token, config.JWT_SECRET, algorithms=[config.JWT_ALGORITHM])