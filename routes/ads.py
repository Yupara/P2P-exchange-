from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from db import models, schemas, database
from auth.auth import get_current_user

router = APIRouter(
    prefix="/ads",
    tags=["ads"]
)

@router.get("/")
def get_ads(db: Session = Depends(database.get_db)):
    return db.query(models.Ad).all()

@router.get("/my")
def get_my_ads(user: models.User = Depends(get_current_user), db: Session = Depends(database.get_db)):
    return db.query(models.Ad).filter(models.Ad.owner_id == user.id).all()

@router.post("/")
def create_ad(ad: schemas.AdCreate, user: models.User = Depends(get_current_user), db: Session = Depends(database.get_db)):
    new_ad = models.Ad(**ad.dict(), owner_id=user.id)
    db.add(new_ad)
    db.commit()
    db.refresh(new_ad)
    return new_ad

@router.put("/{ad_id}")
def update_ad(ad_id: int, ad_data: schemas.AdCreate, user: models.User = Depends(get_current_user), db: Session = Depends(database.get_db)):
    ad = db.query(models.Ad).filter(models.Ad.id == ad_id).first()
    if not ad:
        raise HTTPException(status_code=404, detail="Ad not found")
    if ad.owner_id != user.id:
        raise HTTPException(status_code=403, detail="Not authorized")
    ad.title = ad_data.title
    ad.description = ad_data.description
    ad.price = ad_data.price
    db.commit()
    db.refresh(ad)
    return ad

@router.delete("/{ad_id}")
def delete_ad(ad_id: int, user: models.User = Depends(get_current_user), db: Session = Depends(database.get_db)):
    ad = db.query(models.Ad).filter(models.Ad.id == ad_id).first()
    if not ad:
        raise HTTPException(status_code=404, detail="Ad not found")
    if ad.owner_id != user.id:
        raise HTTPException(status_code=403, detail="Not authorized")
    db.delete(ad)
    db.commit()
    return {"message": "Ad deleted"}
