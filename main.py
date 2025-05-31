from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from jose import jwt, JWTError
from datetime import datetime, timedelta
from passlib.context import CryptContext

# ---------------------------------------------------
# 1. Настройки для JWT
# ---------------------------------------------------
SECRET_KEY = "supersecretkey123"   # Замените на более надёжный секретный ключ
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60    # Срок жизни токена — 60 минут

# Схема безопасности Bearer для Swagger UI
bearer_scheme = HTTPBearer()

# Для хеширования/проверки пароля
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# «База» пользователей в памяти (email → bcrypt-хеш-пароля)
fake_users_db: dict[str, str] = {
    # Пароль для alice@example.com = "secret123" 
    # (хеш сгенерирован заранее командой bcrypt.hash("secret123"))
    "alice@example.com": "$2b$12$7QJH5WgNVv6JjaUbv1CIsewoif4fglRU/5iN9BnzEJI7frUeFSVM."
}
# Соответствие email → id (эмулируем таблицу пользователей)
fake_user_id: dict[str, int] = {
    "alice@example.com": 1
}

# ---------------------------------------------------
# 2. Вспомогательные функции для работы с JWT и паролями
# ---------------------------------------------------
def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Проверяет соответствие plain_password и bcrypt-хеша.
    """
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: dict) -> str:
    """
    Генерирует JWT с любыми полями из data + время жизни (exp).
    Сохраняет в payload ключ "sub" = data["sub"].
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
    Зависимость для проверки Bearer-токена:
      • credentials.credentials — сама JWT-строка без префикса Bearer 
      • Если JWT валидна и в payload есть ключ "sub" (email), возвращаем его.
      • Иначе кидаем HTTPException 401.
    Swagger UI увидит эту зависимость и покажет кнопку "Authorize".
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
    return email

# ---------------------------------------------------
# 3. Pydantic-модели для запросов/ответов
# ---------------------------------------------------
class UserLogin(BaseModel):
    email: str
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str

# ---------------------------------------------------
# 4. Создаём экземпляр FastAPI
# ---------------------------------------------------
app = FastAPI()

# ---------------------------------------------------
# 5. Эндпоинты для логина и получения данных о текущем пользователе
# ---------------------------------------------------
@app.post("/auth/login", response_model=TokenResponse, tags=["auth"])
def login(user_data: UserLogin):
    """
    POST /auth/login
    Тело (JSON): { "email": "...", "password": "..." }
    Если email и пароль верны, возвращает:
      {
        "access_token": "<jwt>",
        "token_type": "bearer"
      }
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
    Возвращает:
      {
        "email": "...",
        "id": <id пользователя>
      }
    """
    return {"email": email, "id": fake_user_id.get(email)}

# ---------------------------------------------------
# 6. Подключаем маршруты из файла ads.py
# ---------------------------------------------------
import ads  
app.include_router(ads.router)
