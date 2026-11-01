
import os

import pytest
from dotenv import load_dotenv

load_dotenv()

test_url = os.getenv("TEST_DATABASE_URL")
main_url = os.getenv("DATABASE_URL")
if not test_url:
    pytest.exit("TEST_DATABASE_URL is not set.")
if test_url == main_url:
    pytest.exit("TEST_DATABASE_URL must be different from DATABASE_URL.")
os.environ["DATABASE_URL"] = test_url  # point the app at the test branch

from fastapi.testclient import TestClient  # noqa: E402

from app.core.security import hash_password  # noqa: E402
from app.infrastructure.database.connection import get_connection  # noqa: E402
from app.main import app  # noqa: E402

USER_EMAIL = "user@example.com"
ADMIN_EMAIL = "admin@example.com"
PASSWORD = "password123"


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture(autouse=True)
def clean_tables():
    with get_connection() as conn:
        conn.execute("TRUNCATE TABLE books, users RESTART IDENTITY")
    yield


def _login(client, email):
    response = client.post("/auth/login", json={"email": email, "password": PASSWORD})
    return {"Authorization": f"Bearer {response.json()['access_token']}"}


@pytest.fixture
def user_headers(client):
    client.post(
        "/auth/register",
        json={"username": "regular", "email": USER_EMAIL, "password": PASSWORD},
    )
    return _login(client, USER_EMAIL)


@pytest.fixture
def admin_headers(client):
    # Admins can't be created through the API, so insert one directly.
    with get_connection() as conn:
        conn.execute(
            "INSERT INTO users (username, email, password_hash, role) "
            "VALUES (%s, %s, %s, 'admin')",
            ("boss", ADMIN_EMAIL, hash_password(PASSWORD)),
        )
    return _login(client, ADMIN_EMAIL)