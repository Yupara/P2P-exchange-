from sqlalchemy.orm import Session
from models import User
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_user_by_username(db: Session, username: str):
    return db.query(User).filter(User.username == username).first()

def get_user_by_email(db: Session, email: str):
    return db.query(User).filter(User.email == email).first()

def create_user(db: Session, username: str, email: str, password: str):
    hashed_password = pwd_context.hash(password)
    user = User(username=username, email=email, hashed_password=hashed_password)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

def authenticate_user(db: Session, username_or_email: str, password: str):
    user = (
        db.query(User)
        .filter((User.username == username_or_email) | (User.email == username_or_email))
        .first()
    )
    if user and pwd_context.verify(password, user.hashed_password):
        return user
    return None
