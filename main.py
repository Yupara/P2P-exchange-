from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from jose import jwt, JWTError
from datetime import datetime, timedelta

# ――――――――― Настройки JWT ―――――――――
SECRET_KEY = "supersecretkey123"  # Замените на собственный сложный ключ
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

# Схема безопасности для Swagger (HTTP Bearer)
bearer_scheme = HTTPBearer()


def create_access_token(data: dict) -> str:
    """
    Генерирует JWT-токен с полем "sub" = data["sub"] и временем жизни ACCESS_TOKEN_EXPIRE_MINUTES.
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
    Проверяет JWT, возвращает поле "sub" (email) или кидает HTTP 401.
    Swagger увидит HTTPBearer и нарисует кнопку "Authorize".
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
    return email  # Дальше, при вызове Depends(verify_token), мы получаем email текущего пользователя


# ――――――――― Модели Pydantic для входа и ответа ―――――――――
class UserLogin(BaseModel):
    email: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str


# ――――――――― “Фейковая” база пользователей ―――――――――
# В реальном проекте вы бы брали из БД: здесь for demo.
# Пример: у нас один пользователь alice@example.com с паролем secret123 (bcrypt-хеш).
fake_users_db: dict[str, str] = {
    "alice@example.com": "$2b$12$7QJH5WgNVv6JjaUbv1CIsewoif4fglRU/5iN9BnzEJI7frUeFSVM."
    # Хеш получен командой: bcrypt.hash("secret123")
}
# И соответствующий ID:
fake_user_id: dict[str, int] = {
    "alice@example.com": 1
}

# Для проверки пароля через bcrypt:
from passlib.context import CryptContext
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


app = FastAPI()


@app.post("/auth/login", response_model=TokenResponse, tags=["auth"])
def login(user_data: UserLogin):
    """
    POST /auth/login
    Body: { "email": "alice@example.com", "password": "secret123" }
    Возвращает JWT, если email и пароль верны.
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
    Возвращает { "email": ..., "id": ... }
    """
    return {"email": email, "id": fake_user_id.get(email)}


# ――――――――― Подключаем маршруты из ads.py ―――――――――
import ads  # Импортирует файл ads.py из той же папки
app.include_router(ads.router)
