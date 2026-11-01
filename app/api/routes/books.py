from typing import Annotated

from fastapi import APIRouter, Depends, Path, Response, status

from app.api.dependencies import (
    get_book_repository,
    get_current_user,
    require_admin,
)
from app.application.use_cases.create_book import CreateBook
from app.application.use_cases.delete_book import DeleteBook
from app.application.use_cases.get_books import GetBook, GetBooks
from app.application.use_cases.update_book import UpdateBook
from app.domain.entities.book import Book
from app.domain.repositories.book_repository import BookRepository
from app.schemas.book import BookBase, BookResponse

router = APIRouter(
    prefix="/books",
    tags=["books"],
    dependencies=[Depends(get_current_user)],  # login required for every route
)

BookId = Annotated[int, Path(gt=0, le=2_147_483_647)]


@router.post("", response_model=BookResponse, status_code=status.HTTP_201_CREATED)
def create_book(book: BookBase, repo: BookRepository = Depends(get_book_repository)):
    return CreateBook(repo).execute(Book(**book.model_dump()))


@router.get("", response_model=list[BookResponse])
def list_books(repo: BookRepository = Depends(get_book_repository)):
    return GetBooks(repo).execute()


@router.get("/{book_id}", response_model=BookResponse)
def get_book(book_id: BookId, repo: BookRepository = Depends(get_book_repository)):
    return GetBook(repo).execute(book_id)


@router.put(
    "/{book_id}",
    response_model=BookResponse,
    dependencies=[Depends(require_admin)],  # admin only
)
def update_book(
    book_id: BookId, book: BookBase, repo: BookRepository = Depends(get_book_repository)
):
    return UpdateBook(repo).execute(book_id, Book(**book.model_dump()))


@router.delete(
    "/{book_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(require_admin)],  # admin only
)
def delete_book(book_id: BookId, repo: BookRepository = Depends(get_book_repository)):
    DeleteBook(repo).execute(book_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)