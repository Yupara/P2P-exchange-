from fastapi import FastAPI
import models
from database import engine
from routes import ads as ads_routes  # Импортируем роуты

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

# Подключаем роуты объявлений
app.include_router(ads_routes.router, prefix="/ads", tags=["ads"])
