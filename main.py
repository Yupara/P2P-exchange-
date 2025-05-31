from fastapi import FastAPI
from database import Base, engine
from auth.routes import router as auth_router
from ads.routes import router as ads_router

Base.metadata.create_all(bind=engine)

app = FastAPI()

app.include_router(auth_router)
app.include_router(ads_router)

@app.get("/")
def root():
    return {"message": "Welcome to the P2P platform!"}
