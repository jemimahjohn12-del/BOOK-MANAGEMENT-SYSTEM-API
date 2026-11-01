from app.domain.entities.book import Book
from app.domain.exceptions import BookNotFoundError
from app.domain.repositories.book_repository import BookRepository


class GetBooks:
    def __init__(self, books: BookRepository):
        self.books = books

    def execute(self) -> list[Book]:
        return self.books.get_all()


class GetBook:
    def __init__(self, books: BookRepository):
        self.books = books

    def execute(self, book_id: int) -> Book:
        book = self.books.get_by_id(book_id)
        if book is None:
            raise BookNotFoundError()
        return book