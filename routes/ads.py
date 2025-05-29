from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
import models
import schemas
import database

router = APIRouter()

@router.post("/ads", response_model=schemas.AdOut)
def create_ad(ad: schemas.AdCreate, db: Session = Depends(database.get_db)):
    db_ad = models.Advertisement(**ad.dict())
    db.add(db_ad)
    db.commit()
    db.refresh(db_ad)
    return db_ad
