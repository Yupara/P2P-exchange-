from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from auth.utils import verify_password, hash_password
from auth.jwt_handler import create_access_token
from schemas import UserCreate, Token, UserOut
from models import User
from auth.deps import get_db, get_current_user

router = APIRouter()

@router.post("/register", response_model=UserOut)
def register(user_data: UserCreate, db: Session = Depends(get_db)):
    existing_user = db.query(User).filter((User.email == user_data.email) | (User.username == user_data.username)).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="User already exists")
    hashed = hash_password(user_data.password)
    user = User(username=user_data.username, email=user_data.email, password=hashed)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

@router.post("/login", response_model=Token)
def login(user_data: UserCreate, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == user_data.email).first()
    if not user or not verify_password(user_data.password, user.password):
        raise HTTPException(status_code=400, detail="Invalid credentials")
    token = create_access_token({"sub": user.username})
    return {"access_token": token, "token_type": "bearer"}

@router.get("/me", response_model=UserOut)
def me(current_user: User = Depends(get_current_user)):
    return current_user
