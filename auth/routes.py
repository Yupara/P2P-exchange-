from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from auth.schemas import UserCreate, UserOut, Token
from auth.services import create_user, authenticate_user, get_user_by_username, get_user_by_email
from auth.jwt_handler import create_access_token
from auth.deps import get_current_user
from database import get_db
from models import User

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/register", response_model=UserOut)
def register(user_data: UserCreate, db: Session = Depends(get_db)):
    if get_user_by_username(db, user_data.username):
        raise HTTPException(status_code=400, detail="Username already exists")
    if get_user_by_email(db, user_data.email):
        raise HTTPException(status_code=400, detail="Email already exists")
    return create_user(db, user_data.username, user_data.email, user_data.password)

@router.post("/login", response_model=Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    token = create_access_token(data={"sub": str(user.id)})
    return {"access_token": token, "token_type": "bearer"}

@router.get("/me", response_model=UserOut)
def me(current_user: User = Depends(get_current_user)):
    return current_user
