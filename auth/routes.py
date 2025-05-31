# auth/routes.py

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from auth.schemas import UserCreate, UserOut, Token
from auth.services import create_user, authenticate_user, get_user_by_username, get_user_by_email
from auth.jwt_handler import create_access_token
from auth.deps import get_current_user
from database import get_db
from models import User

router = APIRouter(
    prefix="/auth",
    tags=["auth"],
)

@router.post("/register", response_model=UserOut, status_code=status.HTTP_201_CREATED)
def register(user_data: UserCreate, db: Session = Depends(get_db)):
    # Проверим, что username и email уникальны
    if get_user_by_username(db, user_data.username):
        raise HTTPException(status_code=400, detail="Username already registered")
    if get_user_by_email(db, user_data.email):
        raise HTTPException(status_code=400, detail="Email already registered")

    new_user = create_user(db, username=user_data.username, email=user_data.email, password=user_data.password)
    if new_user is None:
        raise HTTPException(status_code=500, detail="Error creating user")
    return new_user

@router.post("/login", response_model=Token)
def login(
    username_or_email: str,
    password: str,
    db: Session = Depends(get_db)
):
    """
    Логин по username или email (оба доступны через один параметр),
    возвращает JWT-токен.
    """
    user = authenticate_user(db, username_or_email, password)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

    # В payload кладём user.id
    token = create_access_token(data={"sub": str(user.id)})
    return {"access_token": token, "token_type": "bearer"}

@router.get("/me", response_model=UserOut)
def read_current_user(current_user: User = Depends(get_current_user)):
    """
    Эндпоинт /auth/me — возвращает текущего пользователя по токену.
    """
    return current_user
