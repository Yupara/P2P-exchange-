from fastapi import FastAPI
import ads

app = FastAPI()

app.include_router(ads.router)
