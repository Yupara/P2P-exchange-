# main.py

from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt, JWTError
from datetime import datetime, timedelta
from pydantic import BaseModel
from passlib.context import CryptContext

# ========== 1. Настройки JWT ==========

SECRET_KEY = "supersecretkey123"    # Замените на свой длинный секрет
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60     # например, токен живёт 60 минут

# Пайплайн для bcrypt-паролей
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Схема безопасности для Swagger:
bearer_scheme = HTTPBearer()

# «Фейковая» база пользователей (email → bcrypt-хеш)
fake_users_db: dict[str, str] = {
    "alice@example.com": "$2b$12$7QJH5WgNVv6JjaUbv1CIsewoif4fglRU/5iN9BnzEJI7frUeFSVM."
}
# email → id (эмуляция)
fake_user_id: dict[str, int] = {
    "alice@example.com": 1
}

# ========== 2. Вспомогательные функции ==========

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: dict) -> str:
    """
    Генерирует JWT со сроком жизни ACCESS_TOKEN_EXPIRE_MINUTES.
    Кладёт в payload поле "sub" = data["sub"].
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
    Зависимость, которая проверяет заголовок:
      Authorization: Bearer <ваш_JWT>
    - Декодирует JWT (проверяет подпись, exp и т. д.)
    - Берёт из payload поле "sub" (email)
    - Если всё ок, возвращает email
    - Иначе кидает HTTPException(401)
    
    Благодаря тому, что в параметрах функции стоит Depends(bearer_scheme),
    Swagger UI автоматически нарисует кнопку «Authorize» (🔓) и позволит вам
    вставить ваш токен.
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


# ========== 3. Схемы Pydantic ==========

class UserLogin(BaseModel):
    email: str
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str


# ========== 4. Инициализируем FastAPI ==========

app = FastAPI(title="P2P Exchange API")


@app.post("/auth/login", response_model=TokenResponse, tags=["auth"])
def login(user_data: UserLogin):
    """
    POST /auth/login
    Body (JSON):
      {
        "email": "...",
        "password": "..."
      }
    Если email существует и пароль верный — возвращаем JWT.
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
def get_current_user(email: str = Depends(verify_token)):
    """
    GET /auth/me
    Требует заголовок: Authorization: Bearer <JWT>.
    Если токен валиден, вернётся { "email": email, "id": fake_user_id[email] }.
    """
    return {"email": email, "id": fake_user_id.get(email)}


# ========== 5. Подключаем роуты объявлений ==========

