from fastapi import FastAPI
from auth.routes import router as auth_router
from ads_routes import router as ads_router
from database import Base, engine
from models import *

Base.metadata.create_all(bind=engine)

app = FastAPI(title="P2P Exchange API")

app.include_router(auth_router, prefix="/auth", tags=["auth"])
app.include_router(ads_router, prefix="/ads", tags=["ads"])

@app.get("/")
def root():
    return {"msg": "Welcome to P2P Exchange"}
