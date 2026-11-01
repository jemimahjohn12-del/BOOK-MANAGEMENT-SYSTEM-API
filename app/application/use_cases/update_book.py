from app.domain.entities.book import Book
from app.domain.exceptions import BookNotFoundError
from app.domain.repositories.book_repository import BookRepository


class UpdateBook:
    def __init__(self, books: BookRepository):
        self.books = books

    def execute(self, book_id: int, book: Book) -> Book:
        updated = self.books.update(book_id, book)
        if updated is None:
            raise BookNotFoundError()
        return updated