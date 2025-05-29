# auth/routes.py
from fastapi import APIRouter, Depends, HTTPException, status, Form
from sqlalchemy.orm import Session
from database import get_db
import models, schemas
from auth.jwt_handler import create_access_token, verify_token

router = APIRouter()

@router.post("/register", response_model=schemas.UserOut)
def register(user: schemas.UserCreate, db: Session = Depends(get_db)):
    # … ваша регистрация …
    return services.create_user(db, user.email, user.password)

@router.post("/login")
def login(form_data_email: str = Form(...), form_data_password: str = Form(...),
          db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.email == form_data_email).first()
    if not user or not services.pwd_context.verify(form_data_password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Неверные учётные данные")
    access_token = create_access_token({"sub": user.email})
    return {"access_token": access_token, "token_type": "bearer"}
from fastapi import Depends
from auth.deps import get_current_user
import models, schemas

@router.get("/me", response_model=schemas.UserOut)
def read_users_me(current_user: models.User = Depends(get_current_user)):
    return current_user
