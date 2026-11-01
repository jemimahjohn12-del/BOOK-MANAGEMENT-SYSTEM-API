<<<<<<< HEAD
# Book Management System API

A REST API for managing books, built with **FastAPI** and **PostgreSQL (Neon)**. It supports user registration and login with **JWT authentication**, **role-based authorization** (`user` and `admin`), and full CRUD for books. The code follows **Clean Architecture** so business logic stays separate from the web framework and the database.

## Features

- Register, log in, and view your own profile (`/auth/register`, `/auth/login`, `/auth/me`)
- Passwords hashed with bcrypt, never stored in plain text
- Signed JWT access tokens with an expiry time
- Two roles: `user` (default) and `admin`
- Book CRUD with validation (`/books`)
- An admin-only endpoint (`GET /admin`)
- Database schema managed with migration files
- Automated tests and a Postman collection

## Technologies

Python, FastAPI, PostgreSQL on Neon, Psycopg 3, Pydantic, PyJWT, bcrypt, pytest, golang-migrate, Postman.

## Architecture

The code is split into layers. Each layer only depends on the ones inside it.

| Layer | Folder | Responsibility |
|---|---|---|
| Core | `app/core` | Settings from environment variables, password hashing, JWT creation and checking |
| Domain | `app/domain` | Entities (`Book`, `User`), repository interfaces, domain exceptions. No FastAPI or PostgreSQL code. |
| Application | `app/application/use_cases` | One class per use case (create book, register user, log in, and so on) |
| Infrastructure | `app/infrastructure/database` | Database connection and the PostgreSQL repositories (all SQL lives here) |
| API | `app/api`, `app/schemas` | HTTP routes, request/response schemas, authentication and role checks |

Use cases depend on repository **interfaces** from the domain layer. The PostgreSQL implementations are plugged in by `app/api/dependencies.py`, so the business logic never imports PostgreSQL directly.

## Project structure

```
book-management-system/
├── app/
│   ├── main.py
│   ├── core/            (config.py, security.py)
│   ├── domain/          (entities, repositories, exceptions.py)
│   ├── application/     (use_cases)
│   ├── infrastructure/  (database: connection.py, repositories)
│   ├── schemas/         (book.py, user.py)
│   └── api/             (dependencies.py, routes: books.py, auth.py, admin.py)
├── migrations/          (000001 books, 000002 users: .up.sql and .down.sql)
├── scripts/create_admin.py
├── tests/               (conftest.py, test_auth.py, test_books.py)
├── postman/book-management.postman_collection.json
├── screenshots/
├── .env.example
├── .gitignore
├── pytest.ini
├── requirements.txt
└── README.md
```

## Installation

1. Clone the repository and open the folder.
2. Create and activate a virtual environment:
   ```bash
   python -m venv .venv
   .venv\Scripts\activate        # Windows
   source .venv/bin/activate     # Mac/Linux
   ```
3. Install dependencies:
   ```bash
   python -m pip install -r requirements.txt
   ```

## Environment variables

Copy `.env.example` to `.env` and fill in your own values. **Never commit `.env`.**

| Variable | Purpose |
|---|---|
| `DATABASE_URL` | Neon connection string for the main database |
| `TEST_DATABASE_URL` | Connection string for a separate Neon branch used by the tests |
| `JWT_SECRET` | Long random secret used to sign tokens |
| `JWT_ALGORITHM` | Signing algorithm (`HS256`) |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Token lifetime (`30`) |

Generate a secret with:
```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

Use Neon's **direct** connection string (pooling off), ending in `?sslmode=require`.

## Database migrations

Migrations use [golang-migrate](https://github.com/golang-migrate/migrate). Install it, then run for each database (main and test):

```bash
migrate -path migrations -database "YOUR_CONNECTION_STRING" up
```

Check the applied version:
```bash
migrate -path migrations -database "YOUR_CONNECTION_STRING" version
```

Roll back the latest migration:
```bash
migrate -path migrations -database "YOUR_CONNECTION_STRING" down 1
```

## Running the application

```bash
python -m uvicorn app.main:app --reload
```

The API runs at http://127.0.0.1:8000.

## API documentation

Interactive docs (Swagger UI): http://127.0.0.1:8000/docs

## Creating an admin account

Public registration always creates a `user`; it cannot set a role. To create an administrator, run this script locally. It asks for the details and reads the password without displaying it:

```bash
python -m scripts.create_admin
```

If the email already exists, that account is promoted to admin.

## Using the Postman collection

1. Open Postman and click **Import**.
2. Select `postman/book-management.postman_collection.json`.
3. Make sure the API is running.
4. Open the collection's **Variables** tab. `base_url` is `http://127.0.0.1:8000`. Tokens are empty by default.
5. Register a user, then send **Login**. A script saves the token into `access_token`.
6. Send **Login Admin** (after creating an admin) to save `admin_token`.
7. The requests use these variables as Bearer tokens.

## Running the tests

The tests use a **separate Neon branch**, so your real data is never touched. Create a branch in Neon, apply the migrations to it, and set `TEST_DATABASE_URL` in `.env`. The test setup refuses to run if it equals `DATABASE_URL`.

```bash
python -m pytest -v
```

The tests cover registration, login, duplicate emails, invalid credentials, missing/invalid/expired tokens, role-based access, book CRUD, invalid data and missing books. They can take a few minutes because every test talks to Neon.

## How authentication and authorization work

1. **Register** (`POST /auth/register`): the password is hashed with bcrypt and stored. The role is always `user`.
2. **Login** (`POST /auth/login`): the password is checked against the hash. On success the API returns a signed JWT containing the user's ID (`sub`) and an expiry (`exp`). The same error is returned for a wrong email or a wrong password.
3. **Protected requests**: send the header `Authorization: Bearer <token>`. The API verifies the signature and expiry, then loads the user.
4. **Status codes**: `401` means the token is missing, invalid or expired. `403` means you are logged in but not allowed.

| Operation | User | Admin |
|---|---|---|
| View books (list and by ID) | Allowed | Allowed |
| Create a book | Allowed | Allowed |
| Update a book | 403 | Allowed |
| Delete a book | 403 | Allowed |
| `GET /admin` | 403 | Allowed |

JWT payloads are not encrypted, so no passwords or secrets are placed in them. Use HTTPS in production.

## API endpoints

| Method | Path | Auth | Success | Errors |
|---|---|---|---|---|
| POST | `/auth/register` | None | 201 | 409 duplicate email, 422 invalid data |
| POST | `/auth/login` | None | 200 | 401 invalid credentials |
| GET | `/auth/me` | Token | 200 | 401 |
| POST | `/books` | Token | 201 | 401, 422 |
| GET | `/books` | Token | 200 | 401 |
| GET | `/books/{book_id}` | Token | 200 | 401, 404, 422 |
| PUT | `/books/{book_id}` | Admin | 200 | 401, 403, 404, 422 |
| DELETE | `/books/{book_id}` | Admin | 204 | 401, 403, 404 |
| GET | `/admin` | Admin | 200 | 401, 403 |

## Screenshots

### Successful registration
![Register](screenshots/register.png)

### Successful login
![Login](screenshots/login.png)

### Successful request with an access token (`/auth/me`)
![Auth me](screenshots/auth-me.png)

### Unauthorized request (no token)
![Unauthorized](screenshots/unauthorized.png)

### Regular user denied an admin-only operation
![User forbidden](screenshots/user-forbidden.png)

### Administrator accessing a protected operation
![Admin success](screenshots/admin-success.png)

### Book CRUD
![Create book](screenshots/book-create.png)
![Get books](screenshots/book-list.png)
![Update book](screenshots/book-update.png)
![Delete book](screenshots/book-delete.png)

### Swagger documentation
![Docs](screenshots/docs.png)
NOTE:NOT ALL SCREENSHOTS ARE AVAILABLE
=======
# Book Management System

A robust REST API built with **FastAPI** and **PostgreSQL (hosted on Neon)** for managing a collection of books. This project implements full CRUD (Create, Read, Update, Delete) operations, robust input validation via Pydantic, secure parameter binding using Psycopg, and structured database migrations.

---

 Features

- **RESTful Endpoints:** Full support for creating, retrieving, updating, and deleting books.
- **Persistent Storage:** Data is stored securely in a cloud PostgreSQL database hosted on Neon.
- **Database Migrations:** Version-controlled database schema management using migration scripts (`.up.sql` and `.down.sql`).
- **Data Validation:** Strict input validation and serialization using Pydantic models.
- **Security First:** Protection against SQL injection using parameterized queries, and environment variable isolation for secure configuration.
- **Automated Testing:** Comprehensive test suite for verifying API endpoints.

---

Technologies Used

- **Python 3.10+**
- **FastAPI** (Web framework)
- **Uvicorn** (ASGI server)
- **PostgreSQL & Neon** (Cloud relational database)
- **Psycopg (v3)** (PostgreSQL adapter for Python)
- **Pydantic** (Data validation and settings)
- **Pytest** & **HTTPX** (Automated testing)

---

Project Folder Structure

```text
book-management-system/
│
├── app/
│   ├── __init__.py
│   ├── main.py
│   │
│   ├── database/
│   │   ├── __init__.py
│   │   └── connection.py
│   │
│   ├── models/
│   │   ├── __init__.py
│   │   └── book.py
│   │
│   ├── routes/
│   │   ├── __init__.py
│   │   └── books.py
│   │
│   └── schemas/
│       ├── __init__.py
│       └── book.py
│
├── migrations/
│   ├── 000001_create_books.up.sql
│   └── 000001_create_books.down.sql
│
├── tests/
│   └── test_books.py
│
├── .env.example
├── .gitignore
├── requirements.txt
└── README.md
>>>>>>> 1a954d758e9d6a81b32bec53cdaf4830ec407243
