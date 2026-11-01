from app.domain.repositories.book_repository import BookRepository
from app.infrastructure.database.repositories.postgres_book_repository import (
    PostgresBookRepository,
)


def get_book_repository() -> BookRepository:
    return PostgresBookRepository()