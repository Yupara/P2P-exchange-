from fastapi import FastAPI
from database import Base, engine
from models import *           # создаём все таблицы
from auth.routes import router as auth_router
from ads_routes import router as ads_router

# Генерируем SQLAlchemy-модели (таблицы), если их нет
Base.metadata.create_all(bind=engine)

app = FastAPI(title="P2P Exchange API")

# Регистрируем маршруты для аутентификации
app.include_router(auth_router, prefix="/auth", tags=["auth"])

# Регистрируем маршруты для объявлений
app.include_router(ads_router, prefix="/ads", tags=["ads"])

@app.get("/", tags=["Root"])
def root():
    return {"message": "Welcome to P2P Exchange API"}
