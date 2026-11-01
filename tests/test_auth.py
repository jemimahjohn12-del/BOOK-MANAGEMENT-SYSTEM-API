from datetime import datetime, timedelta, timezone

import jwt

from app.core import config

NEW_USER = {"username": "alice", "email": "alice@example.com", "password": "password123"}


def test_register_success(client):
    response = client.post("/auth/register", json=NEW_USER)
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "alice@example.com"
    assert data["role"] == "user"
    assert "password" not in data
    assert "password_hash" not in data


def test_register_cannot_choose_role(client):
    response = client.post("/auth/register", json={**NEW_USER, "role": "admin"})
    assert response.status_code == 201
    assert response.json()["role"] == "user"


def test_register_duplicate_email_rejected(client):
    client.post("/auth/register", json=NEW_USER)
    response = client.post("/auth/register", json=NEW_USER)
    assert response.status_code == 409


def test_register_duplicate_email_ignores_case(client):
    client.post("/auth/register", json=NEW_USER)
    shouted = {**NEW_USER, "email": "ALICE@example.com"}
    assert client.post("/auth/register", json=shouted).status_code == 409


def test_register_invalid_email(client):
    response = client.post("/auth/register", json={**NEW_USER, "email": "not-an-email"})
    assert response.status_code == 422


def test_register_short_password(client):
    response = client.post("/auth/register", json={**NEW_USER, "password": "short"})
    assert response.status_code == 422


def test_login_success_returns_token(client):
    client.post("/auth/register", json=NEW_USER)
    response = client.post(
        "/auth/login",
        json={"email": NEW_USER["email"], "password": NEW_USER["password"]},
    )
    assert response.status_code == 200
    assert response.json()["access_token"]
    assert response.json()["token_type"] == "bearer"


def test_login_wrong_password_rejected(client):
    client.post("/auth/register", json=NEW_USER)
    response = client.post(
        "/auth/login", json={"email": NEW_USER["email"], "password": "wrongpassword"}
    )
    assert response.status_code == 401


def test_login_error_does_not_reveal_which_part_was_wrong(client):
    client.post("/auth/register", json=NEW_USER)
    wrong_password = client.post(
        "/auth/login", json={"email": NEW_USER["email"], "password": "wrongpassword"}
    )
    unknown_email = client.post(
        "/auth/login", json={"email": "nobody@example.com", "password": "password123"}
    )
    assert wrong_password.status_code == unknown_email.status_code == 401
    assert wrong_password.json() == unknown_email.json()


def test_me_with_valid_token(client, user_headers):
    response = client.get("/auth/me", headers=user_headers)
    assert response.status_code == 200
    assert response.json()["email"] == "user@example.com"
    assert "password_hash" not in response.json()


def test_me_without_token_rejected(client):
    assert client.get("/auth/me").status_code == 401


def test_me_with_invalid_token_rejected(client):
    headers = {"Authorization": "Bearer this.is.not-a-real-token"}
    assert client.get("/auth/me", headers=headers).status_code == 401


def test_me_with_expired_token_rejected(client):
    expired = jwt.encode(
        {"sub": "1", "exp": datetime.now(timezone.utc) - timedelta(minutes=5)},
        config.JWT_SECRET,
        algorithm=config.JWT_ALGORITHM,
    )
    headers = {"Authorization": f"Bearer {expired}"}
    assert client.get("/auth/me", headers=headers).status_code == 401


def test_admin_endpoint_denied_for_regular_user(client, user_headers):
    assert client.get("/admin", headers=user_headers).status_code == 403


def test_admin_endpoint_allowed_for_admin(client, admin_headers):
    assert client.get("/admin", headers=admin_headers).status_code == 200


def test_admin_endpoint_requires_token(client):
    assert client.get("/admin").status_code == 401