from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from auth.deps import get_current_user
import models, schemas

router = APIRouter(prefix="/ads", tags=["Объявления"])

# ➕ Создание объявления
@router.post("/", response_model=schemas.AdOut)
def create_ad(ad: schemas.AdCreate, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    new_ad = models.Ad(**ad.dict(), owner_id=current_user.id)
    db.add(new_ad)
    db.commit()
    db.refresh(new_ad)
    return new_ad

# 🔎 Получение объявлений с фильтрами
@router.get("/", response_model=list[schemas.AdOut])
def get_ads(
    ad_type: str = Query(None, description="buy или sell"),
    currency: str = Query(None, description="например BTC или USDT"),
    min_amount: float = Query(None, description="минимальная сумма"),
    max_amount: float = Query(None, description="максимальная сумма"),
    db: Session = Depends(get_db)
):
    query = db.query(models.Ad)

    if ad_type:
        query = query.filter(models.Ad.ad_type == ad_type)
    if currency:
        query = query.filter(models.Ad.currency == currency)
    if min_amount:
        query = query.filter(models.Ad.amount >= min_amount)
    if max_amount:
        query = query.filter(models.Ad.amount <= max_amount)

    return query.all()

# 👤 Получение только своих объявлений
@router.get("/my", response_model=list[schemas.AdOut])
def get_my_ads(db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    return db.query(models.Ad).filter(models.Ad.owner_id == current_user.id).all()
from fastapi import HTTPException, status

@router.get("/{ad_id}", response_model=schemas.AdOut)
def get_ad(ad_id: int, db: Session = Depends(get_db)):
    ad = db.query(models.Ad).filter(models.Ad.id == ad_id).first()
    if not ad:
        raise HTTPException(status_code=404, detail="Ad not found")
    return ad

@router.delete("/{ad_id}")
def delete_ad(ad_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    ad = db.query(models.Ad).filter(models.Ad.id == ad_id).first()
    if not ad:
        raise HTTPException(status_code=404, detail="Ad not found")
    if ad.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to delete this ad")
    
    db.delete(ad)
    db.commit()
    return {"detail": "Ad deleted"}

@router.put("/{ad_id}", response_model=schemas.AdOut)
def update_ad(ad_id: int, updated_ad: schemas.AdCreate, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    ad = db.query(models.Ad).filter(models.Ad.id == ad_id).first()
    if not ad:
        raise HTTPException(status_code=404, detail="Ad not found")
    if ad.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to update this ad")

    ad.title = updated_ad.title
    ad.description = updated_ad.description
    ad.price = updated_ad.price
    db.commit()
    db.refresh(ad)
    return ad
