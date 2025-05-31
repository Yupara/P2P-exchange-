# main.py

from fastapi import FastAPI
from database import Base, engine
from models import *  # чтобы SQLAlchemy создал таблицы
from auth.routes import router as auth_router
from ads_routes import router as ads_router  # или from ads.routes import router as ads_router, если в папке

Base.metadata.create_all(bind=engine)

app = FastAPI(title="P2P Exchange API")

app.include_router(auth_router, prefix="/auth", tags=["auth"])
app.include_router(ads_router, prefix="/ads", tags=["ads"])

@app.get("/", tags=["Root"])
def root():
    return {"message": "Welcome to P2P Exchange API"}
