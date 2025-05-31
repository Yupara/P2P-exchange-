from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from jose import jwt, JWTError
from datetime import datetime, timedelta
from passlib.context import CryptContext

# ---------------------------------------------------
# 1. Настройки JWT
# ---------------------------------------------------
SECRET_KEY = "supersecretkey123"   # Замените на вашу собственную длинную уникальную строку!
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60    # Токен будет действовать 60 минут

# Схема безопасности HTTP Bearer (для Swagger UI)
bearer_scheme = HTTPBearer()

# Контекст для bcrypt (для хеширования/проверки пароля)
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# «Фейковая» база пользователей (email → bcrypt-хеш пароля)
# В реальном приложении вы бы брали из БД, здесь просто демонстрация
fake_users_db: dict[str, str] = {
    # Пароль для alice@example.com = "secret123"
    # (хешировал заранее: bcrypt.hash("secret123"))
    "alice@example.com": "$2b$12$7QJH5WgNVv6JjaUbv1CIsewoif4fglRU/5iN9BnzEJI7frUeFSVM."
}
# Эмулируем, что у каждого email есть числовой ID (email → id)
fake_user_id: dict[str, int] = {
    "alice@example.com": 1
}


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Проверяет, что plain_password соответствует bcrypt-хешу hashed_password.
    """
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(data: dict) -> str:
    """
    Генерирует JWT, берёт поля из data (ожидается data["sub"] = email),
    добавляет в payload время истечения (exp) и подписывает.
    """
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def verify_token(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme)
) -> str:
    """
    Зависимость для проверки Bearer-токена:
    • FastAPI автоматически достаёт заголовок Authorization: Bearer <JWT>,
      “отрезает” префикс и отдаёт остальную строку в credentials.credentials.
    • Декодируем JWT, проверяем подпись и поле "sub" (email).
    • Если всё ок, возвращаем email; иначе кидаем HTTPException(401).
    Swagger UI увидит, что этот endpoint или роутер зависит от HTTPBearer,
    и сам покажет кнопку “Authorize” (🔓) в /docs.
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
    if not email:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials"
        )
    return email  # Теперь все роуты с Depends(verify_token) получают текущий email


# ---------------------------------------------------
# 2. Pydantic-схемы для логина и возврата токена
# ---------------------------------------------------
class UserLogin(BaseModel):
    email: str
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str


# ---------------------------------------------------
# 3. Запускаем FastAPI-приложение
# ---------------------------------------------------
app = FastAPI()


@app.post("/auth/login", response_model=TokenResponse, tags=["auth"])
def login(user_data: UserLogin):
    """
    POST /auth/login
    Body (JSON): { "email": "...", "password": "..." }
    Если email есть в fake_users_db и пароль совпадает (проверка bcrypt),
    возвращает {"access_token": <jwt>, "token_type": "bearer"}.
    Иначе — HTTP 401.
    """
    hashed_pw = fake_users_db.get(user_data.email)
    if not hashed_pw or not verify_password(user_data.password, hashed_pw):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )
    access_token = create_access_token({"sub": user_data.email})
    return {"access_token": access_token, "token_type": "bearer"}


@app.get("/auth/me", tags=["auth"])
def read_users_me(email: str = Depends(verify_token)):
    """
    GET /auth/me
    Заголовок: Authorization: Bearer <jwt>
    Возвращает { "email": email, "id": fake_user_id[email] }.
    Если заголовок отсутствует или токен некорректен, вернёт 401 Not authenticated.
    """
    return {"email": email, "id": fake_user_id.get(email)}


# ---------------------------------------------------
# 4. Подключаем маршруты из файла ads.py
# ---------------------------------------------------
import ads  # Ключевой момент: файл ads.py **должен лежать рядом** с этим main.py
app.include_router(ads.router)
