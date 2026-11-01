import os

import pytest
from dotenv import load_dotenv

load_dotenv()

test_url = os.getenv("TEST_DATABASE_URL")
if not test_url:
    pytest.exit("TEST_DATABASE_URL is not set.")
os.environ["DATABASE_URL"] = test_url

from fastapi.testclient import TestClient  # noqa: E402

from app.infrastructure.database.connection import get_connection  # noqa: E402
from app.main import app  # noqa: E402


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture(autouse=True)
def clean_table():
    with get_connection() as conn:
        conn.execute("TRUNCATE TABLE books RESTART IDENTITY")
    yield