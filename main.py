from fastapi import FastAPI
from auth.routes import router as auth_router
from routes.ads import router as ads_router
from database import engine
import models

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

app.include_router(auth_router, prefix="/auth")
app.include_router(ads_router, prefix="/ads")
