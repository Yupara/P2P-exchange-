from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database import SessionLocal

router = APIRouter()

@router.get("/")
def read_ads():
    return {"message": "Ads will be here soon"}
