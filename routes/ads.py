from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import models
import schemas
from database import get_db
from auth.deps import get_current_user

router = APIRouter()

@router.post("/", response_model=schemas.AdOut)
def create_ad(
    ad: schemas.AdCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    new_ad = models.Ad(**ad.dict(), owner_id=current_user.id)
    db.add(new_ad)
    db.commit()
    db.refresh(new_ad)
    return new_ad

@router.get("/my-ads", response_model=list[schemas.AdOut])
def get_my_ads(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    return db.query(models.Ad).filter(models.Ad.owner_id == current_user.id).all()

@router.get("/", response_model=list[schemas.AdOut])
def get_all_ads(db: Session = Depends(get_db)):
    return db.query(models.Ad).all()
