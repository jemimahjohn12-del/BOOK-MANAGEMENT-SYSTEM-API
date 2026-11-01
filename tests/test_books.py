VALID_BOOK = {
    "title": "Clean Code",
    "author": "Robert C. Martin",
    "publication_year": 2008,
    "price": 35.50,
    "available": True,
}


def make_book(client, **overrides):
    return client.post("/books", json={**VALID_BOOK, **overrides})


def test_create_book(client):
    response = make_book(client)
    assert response.status_code == 201
    assert response.json()["title"] == "Clean Code"


def test_create_book_rejects_negative_price(client):
    assert make_book(client, price=-1).status_code == 422


def test_get_all_books_empty(client):
    response = client.get("/books")
    assert response.status_code == 200
    assert response.json() == []


def test_get_all_books(client):
    make_book(client)
    make_book(client, title="Refactoring")
    assert len(client.get("/books").json()) == 2


def test_get_book_by_id(client):
    book_id = make_book(client).json()["id"]
    assert client.get(f"/books/{book_id}").status_code == 200


def test_get_missing_book_returns_404(client):
    assert client.get("/books/99999").status_code == 404


def test_update_book(client):
    book_id = make_book(client).json()["id"]
    updated = {**VALID_BOOK, "price": 20.0}
    response = client.put(f"/books/{book_id}", json=updated)
    assert response.status_code == 200
    assert response.json()["price"] == 20.0


def test_update_missing_book_returns_404(client):
    assert client.put("/books/99999", json=VALID_BOOK).status_code == 404


def test_delete_book(client):
    book_id = make_book(client).json()["id"]
    assert client.delete(f"/books/{book_id}").status_code == 204
    assert client.get(f"/books/{book_id}").status_code == 404


def test_delete_missing_book_returns_404(client):
    assert client.delete("/books/99999").status_code == 404