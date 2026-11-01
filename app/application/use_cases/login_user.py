from app.core.security import create_access_token, verify_password
from app.domain.exceptions import InvalidCredentialsError
from app.domain.repositories.user_repository import UserRepository


class LoginUser:
    def __init__(self, users: UserRepository):
        self.users = users

    def execute(self, email: str, password: str) -> str:
        user = self.users.get_by_email(email.lower())
        # Same error for a wrong email and a wrong password, on purpose.
        if user is None or not verify_password(password, user.password_hash):
            raise InvalidCredentialsError()
        return create_access_token(user.id)