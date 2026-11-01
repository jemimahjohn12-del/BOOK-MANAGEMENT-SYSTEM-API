from app.domain.entities.book import Book
from app.domain.repositories.book_repository import BookRepository


class CreateBook:
    def __init__(self, books: BookRepository):
        self.books = books

    def execute(self, book: Book) -> Book:
        return self.books.create(book)