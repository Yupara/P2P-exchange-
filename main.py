from fastapi import FastAPI
from routes import router as ads_router
from auth.auth import router as auth_router
from db import models, database

# Создание базы данных
models.Base.metadata.create_all(bind=database.engine)

app = FastAPI()

# Подключение маршрутов
app.include_router(auth_router)
app.include_router(ads_router)

@app.get("/")
def root():
    return {"message": "Welcome to P2P Exchange API"}
