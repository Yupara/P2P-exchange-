from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from database import get_db
import models
import schemas
from auth.deps import get_current_user

router = APIRouter(prefix="/ads", tags=["Объявления"])

@router.post("/", response_model=schemas.AdOut)
def create_ad(ad: schemas.AdCreate, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    db_ad = models.Ad(**ad.dict(), owner_id=current_user.id)
    db.add(db_ad)
    db.commit()
    db.refresh(db_ad)
    return db_ad

@router.get("/", response_model=List[schemas.AdOut])
def get_ads(
    db: Session = Depends(get_db),
    title: Optional[str] = Query(None),
    min_price: Optional[float] = Query(None),
    max_price: Optional[float] = Query(None),
    owner_id: Optional[int] = Query(None)
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
from auth.deps import get_current_user  # Убедись, что импорт добавлен
from models import User

@router.get("/my", response_model=list[schemas.AdOut])
def read_my_ads(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    my_ads = db.query(models.Ad).filter(models.Ad.owner_id == current_user.id).all()
    return my_ads
