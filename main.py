from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import List
from pydantic import BaseModel
from jose import JWTError, jwt
from datetime import datetime, timedelta

# ―――――――――  Настройки JWT  ―――――――――
SECRET_KEY = "supersecretkey123"   # Замените на вашу сложную секретную строку
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60    # Токен живёт 60 минут

# Схема безопасности для Swagger (HTTP Bearer)
bearer_scheme = HTTPBearer()


def create_access_token(data: dict) -> str:
    """
    Генерирует JWT, клонируя поля data, добавляя время жизни (exp).
    """
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    token = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return token


def verify_token(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme)
) -> str:
    """
    Эта функция вызывается из Depends(bearer_scheme).
    • credentials.credentials — это сама строка JWT без префикса Bearer (fastapi.security её «отрезает»).
    • Если токен корректный и в payload есть поле "sub" (email), возвращаем его.
    • Если что-то не так (просрочен, неверен), кидаем 401.
    """
    token = credentials.credentials
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials"
        )
    email: str = payload.get("sub")
    if email is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials"
        )
    return email  # дальше мы можем использовать email для поиска пользователя


# ――――――――― Примеры моделей (Pydantic) ―――――――――
class UserLogin(BaseModel):
    email: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str


# Для примера: “база” пользователей в памяти (email → password_hash)
fake_users_db: dict[str, str] = {
    # В реальном приложении вы бы хранили пароль в хеше, а не здесь в открытом виде
    "alice@example.com": "$2b$12$7QJH5WgNVv6JjaUbv1CIsewoif4fglRU/5iN9BnzEJI7frUeFSVM.",  # bcrypt("secret123")
}
# id пользователей тоже «эмулируем» (email → id)
fake_user_id: dict[str, int] = {
    "alice@example.com": 1
}


# Функция для хеширования/проверки пароля
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


# ――――――――― Основное приложение ―――――――――
app = FastAPI()


@app.post("/auth/login", response_model=TokenResponse, tags=["auth"])
def login(user_data: UserLogin):
    """
    POST /auth/login
    Body:
        {
          "email": "user@example.com",
          "password": "secret123"
        }
    Если email есть в fake_users_db и пароль совпадает (bcrypt-верификация),
    возвращаем JWT в поле access_token.
    """
    hashed_pw = fake_users_db.get(user_data.email)
    if not hashed_pw or not verify_password(user_data.password, hashed_pw):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )
    # создаём токен, в поле sub запишем email
    access_token = create_access_token({"sub": user_data.email})
    return {"access_token": access_token, "token_type": "bearer"}


@app.get("/auth/me", tags=["auth"])
def read_users_me(email: str = Depends(verify_token)):
    """
    GET /auth/me
    Заголовок: Authorization: Bearer <jwt>
    Если токен валидный, декодируем email из “sub” и возвращаем его.
    """
    return {"email": email, "id": fake_user_id.get(email)}


# ――――――――― Подключаем маршруты из ads.py  ―――――――――
# Здесь мы подключаем все маршруты /ads/*. В них будет
# использоваться Depends(verify_token) (см. ads.py).
import ads
app.include_router(ads.router)
