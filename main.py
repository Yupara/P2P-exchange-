from fastapi import FastAPI
import models
from database import engine
import routes  # routes.py должен быть в том же каталоге

models.Base.metadata.create_all(bind=engine)

app = FastAPI()
app.include_router(routes.router, prefix="/auth", tags=["auth"])
