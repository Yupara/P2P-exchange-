from passlib.context import CryptContext
from sqlalchemy.orm import Session
from models import User
from auth.schemas import UserCreate, UserOut
from fastapi import HTTPException

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def create_user(user_data: UserCreate, db: Session) -> User:
    """
    Создаёт нового пользователя в базе. Если email занят — HTTPException(400).
    """
    existing = db.query(User).filter(User.email == user_data.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")
    hashed = get_password_hash(user_data.password)
    db_user = User(email=user_data.email, hashed_password=hashed)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def authenticate_user(email: str, password: str, db: Session) -> User | None:
    """
    Проверяет email + пароль. Если всё ок — возвращает User, иначе None.
    """
    user = db.query(User).filter(User.email == email).first()
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user
