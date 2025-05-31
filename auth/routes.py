from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from auth.schemas import UserCreate, UserOut, Token
from auth.services import create_user, authenticate_user
from auth.jwt_handler import create_access_token
from auth.deps import get_db, get_current_user

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/register", response_model=UserOut)
def register(user_data: UserCreate, db: Session = Depends(get_db)):
    """
    POST /auth/register
    Создаёт пользователя и возвращает UserOut (id и email).
    """
    return create_user(user_data, db)

@router.post("/login", response_model=Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """
    POST /auth/login
    Форма: username (email) и password.
    Если всё ок — выдаёт JWT.
    """
    user = authenticate_user(form_data.username, form_data.password, db)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    access_token = create_access_token({"sub": user.email})
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/me", response_model=UserOut)
def read_users_me(current_user: User = Depends(get_current_user)):
    """
    GET /auth/me
    Требует Bearer-токен. Возвращает текущего пользователя.
    """
    return current_user
