from fastapi import FastAPI
from models import Base
from database import engine
from auth import router as auth_router

app = FastAPI(title="P2P Exchange API")

Base.metadata.create_all(bind=engine)

app.include_router(auth_router)
