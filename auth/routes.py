from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from auth.schemas import UserCreate, UserOut, Token
from auth.services import create_user, authenticate_user
from auth.jwt_handler import create_token
from auth.deps import get_db, get_current_user
from database import get_db

router = APIRouter()

@router.post("/register", response_model=UserOut)
def register(user_data: UserCreate, db: Session = Depends(get_db)):
    return create_user(db, user_data)

@router.post("/login", response_model=Token)
def login(user_data: UserCreate, db: Session = Depends(get_db)):
    user = authenticate_user(db, user_data.username, user_data.password)
    if not user:
        raise HTTPException(status_code=400, detail="Invalid credentials")
    return {"access_token": create_token(user.id), "token_type": "bearer"}

@router.get("/me", response_model=UserOut)
def get_me(user = Depends(get_current_user)):
    return user
