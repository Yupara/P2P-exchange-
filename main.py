from fastapi import FastAPI
from database import Base, engine
from auth.routes import router as auth_router

Base.metadata.create_all(bind=engine)

app = FastAPI()
app.include_router(auth_router)
