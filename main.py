# main.py

from fastapi import FastAPI
from database import Base, engine
from models import *                      # noqa: F401 (импортирует модели, чтобы SQLAlchemy мог создать таблицы)
from auth.routes import router as auth_router
from ads_routes import router as ads_router   # <-- обязательно ads_routes.py должен лежать рядом

# Генерируем таблицы (если ещё не созданы)
Base.metadata.create_all(bind=engine)

app = FastAPI(title="P2P Exchange API")

# Регистрируем маршруты аутентификации
app.include_router(auth_router, prefix="/auth", tags=["auth"])
# Регистрируем маршруты объявлений
app.include_router(ads_router, prefix="/ads", tags=["ads"])

@app.get("/", tags=["Root"])
def root():
    return {"message": "Welcome to P2P Exchange API"}
