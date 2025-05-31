from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from jose import jwt, JWTError
from datetime import datetime, timedelta
from passlib.context import CryptContext

# ---------------------------------------
# 1) Настройки для JWT
# ---------------------------------------
SECRET_KEY = "supersecretkey123"    # Замените на свою длинную секретную строку!
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60     # Время жизни токена (в минутах)

# Схема безопасности HTTP Bearer (для Swagger)
bearer_scheme = HTTPBearer()

# Контекст для bcrypt
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# «Фейковая» база пользователей: email → bcrypt-хеш(пароля)
# Пароль для alice@example.com = "secret123"
fake_users_db: dict[str, str] = {
    "alice@example.com": "$2b$12$7QJH5WgNVv6JjaUbv1CIsewoif4fglRU/5iN9BnzEJI7frUeFSVM."
}
# email → id (для эмуляции таблицы пользователей)
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
    Генерирует JWT, добавляя в payload поля из data + время истечения (exp).
    Ожидаем, что data содержит key "sub" со значением email.
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
    Зависимость для проверки Bearer-токена.
    • FastAPI достаёт заголовок Authorization: Bearer <JWT>,
      «отрезает» префикс и передаёт сам токен в credentials.credentials.
    • Мы декодируем токен и проверяем, что в payload есть "sub" = email.
    • Если что-то неверно (просрочен, invalid signature или нет sub) →
      кидаем HTTPException(status_code=401). 
    • Иначе возвращаем email, чтобы дальше использовать его в routes.
    Swagger UI увидит эту зависимость и отрисует кнопку “Authorize”.
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
    return email  # При Depends(verify_token) мы получаем email текущего пользователя


# ---------------------------------------
# 2) Pydantic-схемы для запросов и ответов
# ---------------------------------------
class UserLogin(BaseModel):
    email: str
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str


# ---------------------------------------
# 3) Основное приложение FastAPI
# ---------------------------------------
app = FastAPI()


@app.post("/auth/login", response_model=TokenResponse, tags=["auth"])
def login(user_data: UserLogin):
    """
    POST /auth/login
    Body (JSON):
      {
        "email": "alice@example.com",
        "password": "secret123"
      }
    Если email есть в fake_users_db и пароль совпадает (проверка bcrypt),
    возвращаем:
      {
        "access_token": "<jwt>",
        "token_type": "bearer"
      }
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
    Требует заголовок: Authorization: Bearer <jwt>.
    Если токен валиден, возвращает:
      {
        "email": email,
        "id": fake_user_id[email]
      }
    Иначе — 401.
    """
    return {"email": email, "id": fake_user_id.get(email)}


# ---------------------------------------
# 4) Подключаем маршруты из файла ads.py
# ---------------------------------------
import ads   # Файл ads.py должен лежать рядом с main.py
app.include_router(ads.router)
