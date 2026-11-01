from abc import ABC, abstractmethod

from app.domain.entities.book import Book


class BookRepository(ABC):
    @abstractmethod
    def create(self, book: Book) -> Book: ...

    @abstractmethod
    def get_all(self) -> list[Book]: ...

    @abstractmethod
    def get_by_id(self, book_id: int) -> Book | None: ...

    @abstractmethod
    def update(self, book_id: int, book: Book) -> Book | None: ...

    @abstractmethod
    def delete(self, book_id: int) -> bool: ...