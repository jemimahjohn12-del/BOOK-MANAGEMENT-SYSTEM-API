import getpass

from app.core.security import hash_password
from app.infrastructure.database.connection import get_connection


def main() -> None:
    username = input("Admin username: ").strip()
    email = input("Admin email: ").strip().lower()
    password = getpass.getpass("Admin password (min 8 characters): ")

    if len(username) < 3 or "@" not in email:
        print("Invalid username or email.")
        return
    if len(password) < 8 or len(password.encode("utf-8")) > 72:
        print("Password must be 8 to 72 characters.")
        return

    with get_connection() as conn:
        with conn.cursor() as cur:
            # New email: creates an admin. Existing email: promotes that user.
            cur.execute(
                """
                INSERT INTO users (username, email, password_hash, role)
                VALUES (%s, %s, %s, 'admin')
                ON CONFLICT (email) DO UPDATE SET role = 'admin'
                RETURNING id
                """,
                (username, email, hash_password(password)),
            )
            print(f"Admin ready (user id {cur.fetchone()['id']}).")


if __name__ == "__main__":
    main()