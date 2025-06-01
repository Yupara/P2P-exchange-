from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm
from auth.schemas import UserCreate, Token
from auth.dependencies import oauth2_scheme

router = APIRouter()

@router.post("/login", response_model=Token)
def login(form_data: OAuth2PasswordRequestForm = Depends()):
    # Просто возвращаем фейковый токен (для теста Swagger)
    return {
        "access_token": "fake-jwt-token",
        "token_type": "bearer"
    }

@router.get("/me")
def read_users_me(token: str = Depends(oauth2_scheme)):
    return {"user": "current", "token": token}
