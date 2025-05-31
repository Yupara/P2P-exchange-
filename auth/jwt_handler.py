from datetime import datetime, timedelta
from jose import jwt, JWTError

SECRET_KEY = "mysecret"
ALGORITHM = "HS256"
EXPIRE_MINUTES = 60

def create_token(user_id: int):
    expire = datetime.utcnow() + timedelta(minutes=EXPIRE_MINUTES)
    payload = {"sub": user_id, "exp": expire}
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

def decode_token(token: str):
    return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
