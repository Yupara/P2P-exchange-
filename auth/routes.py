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
    Регистрация нового пользователя. 
    Если email уже есть — 400. Возвращает UserOut {id, email}.
    """
    return create_user(user_data, db)

@router.post("/login", response_model=Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """
    POST /auth/login
    Форма: username (email) и password.
    Возвращает JWT Token {"access_token", "token_type"}.
    """
    user = authenticate_user(form_data.username, form_data.password, db)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    # создаём JWT, в payload кладём {"sub": email}
    token = create_access_token({"sub": user.email})
    return {"access_token": token, "token_type": "bearer"}

@router.get("/me", response_model=UserOut)
def read_users_me(current_user: User = Depends(get_current_user)):
    """
    GET /auth/me
    Требует заголовок Authorization: Bearer <token>.
    Возвращает текущего пользователя {id, email}.
    """
    return current_user
