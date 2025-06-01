from fastapi import FastAPI
from fastapi.security import OAuth2PasswordBearer
from auth.routes import router as auth_router

app = FastAPI()

app.include_router(auth_router, prefix="/auth")
