from datetime import datetime, timedelta
from jose import jwt
from config import SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES

def create_access_token(data: dict) -> str:
    """
    Генерирует JWT, в payload кладёт все ключи из data,
    а также добавляет ключ "exp" (время истечения).
    В data мы обязательно передадим {"sub": email}.
    """
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def decode_access_token(token: str) -> dict:
    """
    Декодирует JWT и возвращает payload. Если токен невалидный — исключение.
    """
    return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
