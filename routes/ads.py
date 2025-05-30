# routes/ads.py

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

import models, schemas
from database import get_db
from auth.deps import get_current_user

router = APIRouter(tags=["Объявления"])

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

@router.get("/", response_model=list[schemas.AdOut])
def get_ads(
    db: Session = Depends(get_db),
    title: str = Query(None),
    min_price: float = Query(None),
    max_price: float = Query(None),
    owner_id: int = Query(None)
):
    query = db.query(models.Ad)

    if title:
        query = query.filter(models.Ad.title.ilike(f"%{title}%"))
    if min_price is not None:
        query = query.filter(models.Ad.price >= min_price)
    if max_price is not None:
        query = query.filter(models.Ad.price <= max_price)
    if owner_id:
        query = query.filter(models.Ad.owner_id == owner_id)

    return query.all()

@router.get("/my", response_model=list[schemas.AdOut])
def read_my_ads(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    return db.query(models.Ad).filter(models.Ad.owner_id == current_user.id).all()

@router.get("/{ad_id}", response_model=schemas.AdOut)
def read_ad(
    ad_id: int,
    db: Session = Depends(get_db)
):
    ad = db.query(models.Ad).filter(models.Ad.id == ad_id).first()
    if not ad:
        raise HTTPException(status_code=404, detail="Ad not found")
    return ad

@router.put("/{ad_id}", response_model=schemas.AdOut)
def update_ad(
    ad_id: int,
    updated: schemas.AdCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    ad = db.query(models.Ad).filter(models.Ad.id == ad_id).first()
    if not ad:
        raise HTTPException(status_code=404, detail="Ad not found")
    if ad.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to update this ad")

    for field, value in updated.dict().items():
        setattr(ad, field, value)
    db.commit()
    db.refresh(ad)
    return ad

@router.delete("/{ad_id}")
def delete_ad(
    ad_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    ad = db.query(models.Ad).filter(models.Ad.id == ad_id).first()
    if not ad:
        raise HTTPException(status_code=404, detail="Ad not found")
    if ad.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to delete this ad")

    db.delete(ad)
    db.commit()
    return {"detail": "Ad deleted"}
