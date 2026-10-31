# Book Management System

A robust REST API built with **FastAPI** and **PostgreSQL (hosted on Neon)** for managing a collection of books. This project implements full CRUD (Create, Read, Update, Delete) operations, robust input validation via Pydantic, secure parameter binding using Psycopg, and structured database migrations.

---

## 🌟 Features

- **RESTful Endpoints:** Full support for creating, retrieving, updating, and deleting books.
- **Persistent Storage:** Data is stored securely in a cloud PostgreSQL database hosted on Neon.
- **Database Migrations:** Version-controlled database schema management using migration scripts (`.up.sql` and `.down.sql`).
- **Data Validation:** Strict input validation and serialization using Pydantic models.
- **Security First:** Protection against SQL injection using parameterized queries, and environment variable isolation for secure configuration.
- **Automated Testing:** Comprehensive test suite for verifying API endpoints.

---

## 🛠️ Technologies Used

- **Python 3.10+**
- **FastAPI** (Web framework)
- **Uvicorn** (ASGI server)
- **PostgreSQL & Neon** (Cloud relational database)
- **Psycopg (v3)** (PostgreSQL adapter for Python)
- **Pydantic** (Data validation and settings)
- **Pytest** & **HTTPX** (Automated testing)

---

## 📁 Project Folder Structure

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
![API Documentation and Successful Request](assets/api.png)