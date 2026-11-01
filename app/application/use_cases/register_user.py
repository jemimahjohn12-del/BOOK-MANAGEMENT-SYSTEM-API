from app.core.security import hash_password
from app.domain.entities.user import User
from app.domain.exceptions import UserAlreadyExistsError
from app.domain.repositories.user_repository import UserRepository


class RegisterUser:
    def __init__(self, users: UserRepository):
        self.users = users

    def execute(self, username: str, email: str, password: str) -> User:
        email = email.lower()
        if self.users.get_by_email(email) is not None:
            raise UserAlreadyExistsError()
        user = User(username=username, email=email, password_hash=hash_password(password))
        return self.users.create(user)