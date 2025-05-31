from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from auth.deps import get_db, get_current_user
from users.models import User
from users.schemas import UserRead

router = APIRouter(
    prefix="/auth",
    tags=["Auth"],
)

@router.get("/me", response_model=UserRead)
def read_users_me(current_user: User = Depends(get_current_user)):
    return current_user
