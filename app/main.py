import logging

import psycopg
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.api.routes import books
from app.domain.exceptions import (
    BookNotFoundError,
    InvalidCredentialsError,
    UserAlreadyExistsError,
)

logger = logging.getLogger(__name__)

app = FastAPI(title="Book Management System")
from app.api.routes import admin, auth, books
app.include_router(auth.router)
app.include_router(books.router)
app.include_router(admin.router)


@app.exception_handler(BookNotFoundError)
async def book_not_found(request: Request, exc: BookNotFoundError):
    return JSONResponse(status_code=404, content={"detail": "Book not found"})


@app.exception_handler(UserAlreadyExistsError)
async def user_exists(request: Request, exc: UserAlreadyExistsError):
    return JSONResponse(status_code=409, content={"detail": "Email already registered"})


@app.exception_handler(InvalidCredentialsError)
async def invalid_credentials(request: Request, exc: InvalidCredentialsError):
    return JSONResponse(
        status_code=401,
        content={"detail": "Invalid email or password"},
        headers={"WWW-Authenticate": "Bearer"},
    )


@app.exception_handler(psycopg.OperationalError)
async def db_connection_error(request: Request, exc: psycopg.OperationalError):
    logger.error("Database connection error", exc_info=exc)
    return JSONResponse(status_code=503, content={"detail": "Service temporarily unavailable"})


@app.exception_handler(psycopg.Error)
async def db_error(request: Request, exc: psycopg.Error):
    logger.error("Database error", exc_info=exc)
    return JSONResponse(status_code=500, content={"detail": "A database error occurred"})