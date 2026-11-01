from fastapi import APIRouter, Depends, status

from app.api.dependencies import get_current_user, get_user_repository
from app.application.use_cases.login_user import LoginUser
from app.application.use_cases.register_user import RegisterUser
from app.domain.entities.user import User
from app.domain.repositories.user_repository import UserRepository
from app.schemas.user import TokenResponse, UserLogin, UserRegister, UserResponse

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register(data: UserRegister, users: UserRepository = Depends(get_user_repository)):
    return RegisterUser(users).execute(data.username, data.email, data.password)


@router.post("/login", response_model=TokenResponse)
def login(data: UserLogin, users: UserRepository = Depends(get_user_repository)):
    token = LoginUser(users).execute(data.email, data.password)
    return TokenResponse(access_token=token)


@router.get("/me", response_model=UserResponse)
def me(current_user: User = Depends(get_current_user)):
    return current_user