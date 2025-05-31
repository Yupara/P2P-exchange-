# main.py

from fastapi import FastAPI
from database import Base, engine
from models import *  # noqa: импортируем модели, чтобы SQLAlchemy создал таблицы
from auth.routes import router as auth_router
from ads_routes import router as ads_router

# Создаём все таблицы (если их ещё нет)
Base.metadata.create_all(bind=engine)

app = FastAPI(title="P2P Exchange API")

# Роуты
app.include_router(auth_router, prefix="/auth", tags=["auth"])
app.include_router(ads_router, prefix="/ads", tags=["ads"])

@app.get("/", tags=["root"])
def root():
    return {"message": "P2P Exchange API работает!"}
