from fastapi import FastAPI
from database import Base, engine
from models import *  # noqa
from auth.routes import router as auth_router
from ads_routes import router as ads_router

Base.metadata.create_all(bind=engine)

app = FastAPI(title="P2P API")

app.include_router(auth_router, prefix="/auth", tags=["auth"])
app.include_router(ads_router, prefix="/ads", tags=["ads"])

@app.get("/")
def root():
    return {"message": "P2P API working"}
