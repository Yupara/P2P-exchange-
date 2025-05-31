from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from auth.deps import get_db, get_current_user
import models, schemas

router = APIRouter(prefix="/ads", tags=["ads"])

@router.post("/", response_model=schemas.AdOut)
def create_ad(ad_data: schemas.AdCreate, db: Session = Depends(get_db), user: models.User = Depends(get_current_user)):
    ad = models.Ad(**ad_data.dict(), owner_id=user.id)
    db.add(ad)
    db.commit()
    db.refresh(ad)
    return ad

@router.get("/", response_model=list[schemas.AdOut])
def get_all_ads(db: Session = Depends(get_db)):
    return db.query(models.Ad).all()

@router.get("/my", response_model=list[schemas.AdOut])
def get_my_ads(db: Session = Depends(get_db), user: models.User = Depends(get_current_user)):
    return db.query(models.Ad).filter(models.Ad.owner_id == user.id).all()

@router.put("/{ad_id}", response_model=schemas.AdOut)
def update_ad(ad_id: int, ad_data: schemas.AdCreate, db: Session = Depends(get_db), user: models.User = Depends(get_current_user)):
    ad = db.query(models.Ad).get(ad_id)
    if not ad or ad.owner_id != user.id:
        raise HTTPException(status_code=403, detail="Not authorized")
    for key, value in ad_data.dict().items():
        setattr(ad, key, value)
    db.commit()
    return ad

@router.delete("/{ad_id}")
def delete_ad(ad_id: int, db: Session = Depends(get_db), user: models.User = Depends(get_current_user)):
    ad = db.query(models.Ad).get(ad_id)
    if not ad or ad.owner_id != user.id:
        raise HTTPException(status_code=403, detail="Not authorized")
    db.delete(ad)
    db.commit()
    return {"detail": "Ad deleted"}
