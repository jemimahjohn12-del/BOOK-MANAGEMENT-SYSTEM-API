import psycopg

from app.domain.entities.user import User
from app.domain.exceptions import UserAlreadyExistsError
from app.domain.repositories.user_repository import UserRepository
from app.infrastructure.database.connection import get_connection

COLUMNS = "id, username, email, password_hash, role, created_at"


class PostgresUserRepository(UserRepository):
    def create(self, user: User) -> User:
        # The role is never inserted here: the database default ('user') applies.
        try:
            with get_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute(
                        f"""
                        INSERT INTO users (username, email, password_hash)
                        VALUES (%s, %s, %s)
                        RETURNING {COLUMNS}
                        """,
                        (user.username, user.email, user.password_hash),
                    )
                    return User(**cur.fetchone())
        except psycopg.errors.UniqueViolation:
            raise UserAlreadyExistsError()

    def get_by_email(self, email: str) -> User | None:
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(f"SELECT {COLUMNS} FROM users WHERE email = %s", (email,))
                row = cur.fetchone()
                return User(**row) if row else None

    def get_by_id(self, user_id: int) -> User | None:
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(f"SELECT {COLUMNS} FROM users WHERE id = %s", (user_id,))
                row = cur.fetchone()
                return User(**row) if row else None