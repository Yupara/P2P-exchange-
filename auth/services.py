# auth/services.py

import models              # импортируем нашу модель User из models.py
import schemas             # импортируем pydantic-схемы из schemas.py
from database import SessionLocal  # импортируем сессию для работы с БД
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def create_user(email: str, password: str):
    db = SessionLocal()
    hashed = pwd_context.hash(password)
    user = models.User(email=email, hashed_password=hashed)
    db.add(user)
    db.commit()
    db.refresh(user)
    db.close()
    return user
