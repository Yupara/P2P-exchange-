from fastapi import FastAPI
import models
from database import engine
import routes  # просто routes без auth

models.Base.metadata.create_all(bind=engine)

app = FastAPI()
app.include_router(routes.router, prefix="/auth", tags=["auth"])
