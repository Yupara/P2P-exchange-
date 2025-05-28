from fastapi import FastAPI
from database import engine
import models
import routes

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

app.include_router(routes.router, prefix="/auth", tags=["auth"])
