from app.domain.exceptions import BookNotFoundError
from app.domain.repositories.book_repository import BookRepository


class DeleteBook:
    def __init__(self, books: BookRepository):
        self.books = books

    def execute(self, book_id: int) -> None:
        if not self.books.delete(book_id):
            raise BookNotFoundError()