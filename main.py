from fastapi import FastAPI
import models
from database import engine
from auth import routes as auth_routes  # подключаем роуты

models.Base.metadata.create_all(bind=engine)

app = FastAPI()
app.include_router(auth_routes.router, prefix="/auth", tags=["auth"])
