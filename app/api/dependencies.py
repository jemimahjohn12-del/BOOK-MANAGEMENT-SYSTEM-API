import jwt
from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.core.security import decode_access_token
from app.domain.entities.user import User
from app.domain.repositories.book_repository import BookRepository
from app.domain.repositories.user_repository import UserRepository
from app.infrastructure.database.repositories.postgres_book_repository import (
    PostgresBookRepository,
)
from app.infrastructure.database.repositories.postgres_user_repository import (
    PostgresUserRepository,
)

bearer_scheme = HTTPBearer(auto_error=False)


def get_book_repository() -> BookRepository:
    return PostgresBookRepository()


def get_user_repository() -> UserRepository:
    return PostgresUserRepository()


def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
    users: UserRepository = Depends(get_user_repository),
) -> User:
    unauthorized = HTTPException(
        status_code=401,
        detail="Invalid or missing token",
        headers={"WWW-Authenticate": "Bearer"},
    )
    if credentials is None:
        raise unauthorized
    try:
        payload = decode_access_token(credentials.credentials)
        user_id = int(payload["sub"])
    except (jwt.PyJWTError, KeyError, ValueError):
        raise unauthorized
    user = users.get_by_id(user_id)
    if user is None:
        raise unauthorized
    return user
def require_admin(current_user: User = Depends(get_current_user)) -> User:
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    return current_user