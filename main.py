from fastapi import FastAPI
from routes.ads import router as ads_router
from auth.routes import router as auth_router
import models
from database import engine

# Создаём таблицы в БД
models.Base.metadata.create_all(bind=engine)

app = FastAPI()

# Корневой маршрут
@app.get("/")
def root():
    return {"message": "Welcome to P2P Exchange API"}

# Роуты авторизации
app.include_router(auth_router, prefix="/auth", tags=["auth"])
# Роуты объявлений
app.include_router(ads_router, prefix="/ads", tags=["ads"])
