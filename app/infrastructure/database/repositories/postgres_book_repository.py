from app.domain.entities.book import Book
from app.domain.repositories.book_repository import BookRepository
from app.infrastructure.database.connection import get_connection

COLUMNS = "id, title, author, publication_year, price, available"


class PostgresBookRepository(BookRepository):
    def create(self, book: Book) -> Book:
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    f"""
                    INSERT INTO books (title, author, publication_year, price, available)
                    VALUES (%s, %s, %s, %s, %s)
                    RETURNING {COLUMNS}
                    """,
                    (book.title, book.author, book.publication_year,
                     book.price, book.available),
                )
                return Book(**cur.fetchone())

    def get_all(self) -> list[Book]:
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(f"SELECT {COLUMNS} FROM books ORDER BY id")
                return [Book(**row) for row in cur.fetchall()]

    def get_by_id(self, book_id: int) -> Book | None:
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(f"SELECT {COLUMNS} FROM books WHERE id = %s", (book_id,))
                row = cur.fetchone()
                return Book(**row) if row else None

    def update(self, book_id: int, book: Book) -> Book | None:
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    f"""
                    UPDATE books
                    SET title = %s, author = %s, publication_year = %s,
                        price = %s, available = %s
                    WHERE id = %s
                    RETURNING {COLUMNS}
                    """,
                    (book.title, book.author, book.publication_year,
                     book.price, book.available, book_id),
                )
                row = cur.fetchone()
                return Book(**row) if row else None

    def delete(self, book_id: int) -> bool:
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("DELETE FROM books WHERE id = %s", (book_id,))
                return cur.rowcount > 0