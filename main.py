from fastapi import FastAPI
from routes.ads import router as ads_router  # <-- ВАЖНО: ads, а не просто routes

app = FastAPI()

app.include_router(ads_router)
