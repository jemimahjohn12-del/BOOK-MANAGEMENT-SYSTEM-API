VALID_BOOK = {
    "title": "Clean Code",
    "author": "Robert C. Martin",
    "publication_year": 2008,
    "price": 35.50,
    "available": True,
}


def make_book(client, headers, **overrides):
    return client.post("/books", json={**VALID_BOOK, **overrides}, headers=headers)


# ---------- authentication ----------

def test_books_require_token(client):
    assert client.get("/books").status_code == 401
    assert client.post("/books", json=VALID_BOOK).status_code == 401
    assert client.get("/books/1").status_code == 401
    assert client.put("/books/1", json=VALID_BOOK).status_code == 401
    assert client.delete("/books/1").status_code == 401


# ---------- regular user ----------

def test_user_can_create_book(client, user_headers):
    response = make_book(client, user_headers)
    assert response.status_code == 201
    assert response.json()["id"] > 0
    assert response.json()["title"] == "Clean Code"


def test_available_defaults_to_true(client, user_headers):
    body = {k: v for k, v in VALID_BOOK.items() if k != "available"}
    response = client.post("/books", json=body, headers=user_headers)
    assert response.status_code == 201
    assert response.json()["available"] is True


def test_user_can_list_books(client, user_headers):
    assert client.get("/books", headers=user_headers).json() == []
    make_book(client, user_headers)
    make_book(client, user_headers, title="Refactoring")
    assert len(client.get("/books", headers=user_headers).json()) == 2


def test_user_can_get_book_by_id(client, user_headers):
    book_id = make_book(client, user_headers).json()["id"]
    response = client.get(f"/books/{book_id}", headers=user_headers)
    assert response.status_code == 200
    assert response.json()["title"] == "Clean Code"


def test_user_cannot_update_book(client, user_headers):
    book_id = make_book(client, user_headers).json()["id"]
    response = client.put(f"/books/{book_id}", json=VALID_BOOK, headers=user_headers)
    assert response.status_code == 403


def test_user_cannot_delete_book(client, user_headers):
    book_id = make_book(client, user_headers).json()["id"]
    assert client.delete(f"/books/{book_id}", headers=user_headers).status_code == 403
    # the book is still there
    assert client.get(f"/books/{book_id}", headers=user_headers).status_code == 200


# ---------- admin ----------

def test_admin_can_update_book(client, user_headers, admin_headers):
    book_id = make_book(client, user_headers).json()["id"]
    updated = {**VALID_BOOK, "price": 20.0, "publication_year": None}
    response = client.put(f"/books/{book_id}", json=updated, headers=admin_headers)
    assert response.status_code == 200
    assert response.json()["price"] == 20.0
    assert response.json()["publication_year"] is None


def test_admin_can_delete_book(client, user_headers, admin_headers):
    book_id = make_book(client, user_headers).json()["id"]
    assert client.delete(f"/books/{book_id}", headers=admin_headers).status_code == 204
    assert client.get(f"/books/{book_id}", headers=admin_headers).status_code == 404


# ---------- missing books and invalid data ----------

def test_get_missing_book_returns_404(client, user_headers):
    assert client.get("/books/99999", headers=user_headers).status_code == 404


def test_update_missing_book_returns_404(client, admin_headers):
    response = client.put("/books/99999", json=VALID_BOOK, headers=admin_headers)
    assert response.status_code == 404


def test_delete_missing_book_returns_404(client, admin_headers):
    assert client.delete("/books/99999", headers=admin_headers).status_code == 404


def test_invalid_book_id_rejected(client, user_headers):
    assert client.get("/books/abc", headers=user_headers).status_code == 422
    assert client.get("/books/0", headers=user_headers).status_code == 422


def test_negative_price_rejected(client, user_headers):
    assert make_book(client, user_headers, price=-1).status_code == 422


def test_missing_title_rejected(client, user_headers):
    body = {k: v for k, v in VALID_BOOK.items() if k != "title"}
    assert client.post("/books", json=body, headers=user_headers).status_code == 422


def test_title_too_long_rejected(client, user_headers):
    assert make_book(client, user_headers, title="x" * 201).status_code == 422
