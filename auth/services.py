# auth/services.py

from sqlalchemy.orm import Session
from auth.utils import hash_password, verify_password
from models import User

def get_user_by_username(db: Session, username: str) -> User | None:
    return db.query(User).filter(User.username == username).first()

def get_user_by_email(db: Session, email: str) -> User | None:
    return db.query(User).filter(User.email == email).first()

def create_user(db: Session, username: str, email: str, password: str) -> User:
    # Перед созданием проверим, что такого username/email нет
    existing = db.query(User).filter((User.username == username) | (User.email == email)).first()
    if existing:
        # Caller будет ловить эту ситуацию и возвращать 400
        return None
    hashed = hash_password(password)
    user = User(username=username, email=email, hashed_password=hashed)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

def authenticate_user(db: Session, username_or_email: str, password: str) -> User | None:
    # Сначала заберём по username, если не нашли — по email
    user = db.query(User).filter(User.username == username_or_email).first()
    if not user:
        user = db.query(User).filter(User.email == username_or_email).first()
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user
