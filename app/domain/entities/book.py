from dataclasses import dataclass


@dataclass
class Book:
    title: str
    author: str
    price: float
    publication_year: int | None = None
    available: bool = True
    id: int | None = None