from dataclasses import dataclass
from datetime import datetime


@dataclass
class User:
    username: str
    email: str
    password_hash: str
    role: str = "user"
    id: int | None = None
    created_at: datetime | None = None