# auth/jwt_handler.py

from datetime import datetime, timedelta
from jose import jwt, JWTError
from config import SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES

def create_access_token(data: dict) -> str:
    """
    Генерирует JWT-токен с данными в payload.
    В payload мы помещаем, например, {"sub": user_id}.
    """
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def decode_token(token: str) -> dict:
    """
    Возвращает payload (payload["sub"] --> user_id),
    или бросает исключение JWTError, если токен недействителен/просрочен.
    """
    return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
