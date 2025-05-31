from sqlalchemy.orm import Session
from passlib.hash import bcrypt
from models import User

def get_user_by_username(db: Session, username: str):
    return db.query(User).filter(User.username == username).first()

def get_user_by_email(db: Session, email: str):
    return db.query(User).filter(User.email == email).first()

def create_user(db: Session, username: str, email: str, password: str):
    hashed_password = bcrypt.hash(password)
    new_user = User(username=username, email=email, password=hashed_password)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

def authenticate_user(db: Session, username_or_email: str, password: str):
    user = db.query(User).filter((User.username == username_or_email) | (User.email == username_or_email)).first()
    if not user or not bcrypt.verify(password, user.password):
        return None
    return user
