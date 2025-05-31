# auth/routes.py

from fastapi import APIRouter, Depends, HTTPException, status, Form
from sqlalchemy.orm import Session
from database import get_db        # Импортируем из корня
from auth.utils import get_current_user  # Если в utils.py обёртка для декодирования JWT
from auth.jwt_handler import create_access_token  # Чтобы генерировать токены
import models
import schemas
from passlib.context import CryptContext

router = APIRouter(prefix="/auth", tags=["auth"])
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# ------------------------------------------
# 1) Регистрация нового пользователя (примерно)
# ------------------------------------------
@router.post("/register", response_model=schemas.UserOut)
def register(
    email: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db)
):
    # Проверяем, есть ли пользователь с таким email
    existing = db.query(models.User).filter(models.User.email == email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")
    hashed_password = pwd_context.hash(password)
    new_user = models.User(email=email, hashed_password=hashed_password)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

# ------------------------------------------
# 2) Логин: выдаём JWT
# ------------------------------------------
@router.post("/login", response_model=schemas.TokenResponse)
def login(
    email: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db)
):
    user = db.query(models.User).filter(models.User.email == email).first()
    if not user or not pwd_context.verify(password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    token = create_access_token({"sub": user.email})
    return {"access_token": token, "token_type": "bearer"}

# ------------------------------------------
# 3) Эндпоинт “/me”: вернёт текущего пользователя
# ------------------------------------------
@router.get("/me", response_model=schemas.UserOut)
def read_users_me(current_user: models.User = Depends(get_current_user)):
    """
    GET /auth/me
    Требует Bearer-токен в заголовке. Если токен валидный, get_current_user 
    достанет пользователя из БД и вернёт его.
    """
    return current_user
