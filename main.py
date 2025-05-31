from fastapi import FastAPI
from auth.routes import router as auth_router
from ads.routes import router as ads_router  # <-- если папка ads и в ней routes.py
from database import Base, engine

Base.metadata.create_all(bind=engine)

app = FastAPI()

app.include_router(auth_router, prefix="/auth", tags=["auth"])
app.include_router(ads_router, prefix="/ads", tags=["ads"])
