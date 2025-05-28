from fastapi import FastAPI
from .auth import routes as auth_routes
from .ads_routes import router as ads_router  # если ты сохранишь как ads_routes.py

app = FastAPI()

app.include_router(auth_routes.router, prefix="/auth", tags=["auth"])
app.include_router(ads_router, prefix="/ads", tags=["ads"])
