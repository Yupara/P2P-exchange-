from fastapi import FastAPI
import models
from database import engine
from routes.ads import router as ads_router
from auth.routes import router as auth_router

models.Base.metadata.create_all(bind=engine)

app = FastAPI()
app.include_router(auth_router, prefix="/auth", tags=["auth"])
app.include_router(ads_router, prefix="/ads", tags=["ads"])
