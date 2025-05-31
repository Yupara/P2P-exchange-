from fastapi import FastAPI
from db import models, database
from auth.auth import router as auth_router
from routes.ads import router as ads_router

models.Base.metadata.create_all(bind=database.engine)

app = FastAPI()

app.include_router(auth_router)
app.include_router(ads_router)

@app.get("/")
def root():
    return {"message": "Welcome to P2P Exchange API"}
