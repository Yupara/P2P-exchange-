# ads/routes.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from ads.schemas import AdCreate, AdOut, AdUpdate
from models import Ad
from auth.deps import get_current_user
from database import get_db
from models import User

router = APIRouter()

@router.post("/", response_model=AdOut)
def create_ad(ad: AdCreate, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    new_ad = Ad(**ad.dict(), owner_id=user.id)
    db.add(new_ad)
    db.commit()
    db.refresh(new_ad)
    return new_ad

@router.get("/", response_model=List[AdOut])
def get_all_ads(db: Session = Depends(get_db)):
    return db.query(Ad).all()

@router.get("/my", response_model=List[AdOut])
def get_my_ads(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return db.query(Ad).filter(Ad.owner_id == user.id).all()

@router.put("/{ad_id}", response_model=AdOut)
def update_ad(ad_id: int, updated: AdUpdate, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    ad = db.query(Ad).filter(Ad.id == ad_id).first()
    if not ad or ad.owner_id != user.id:
        raise HTTPException(status_code=404, detail="Ad not found or not yours")

    for field, value in updated.dict().items():
        setattr(ad, field, value)

    db.commit()
    db.refresh(ad)
    return ad

@router.delete("/{ad_id}", status_code=204)
def delete_ad(ad_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    ad = db.query(Ad).filter(Ad.id == ad_id).first()
    if not ad or ad.owner_id != user.id:
        raise HTTPException(status_code=404, detail="Ad not found or not yours")

    db.delete(ad)
    db.commit()
    return
