from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from auth.utils import get_current_user
from models import Ad, User
from schemas import AdCreate, AdOut

router = APIRouter()

# ➕ Создание объявления
@router.post("/", response_model=AdOut)
def create_ad(ad: AdCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    new_ad = Ad(**ad.dict(), owner_id=current_user.id)
    db.add(new_ad)
    db.commit()
    db.refresh(new_ad)
    return new_ad

# 📋 Получение всех объявлений
@router.get("/", response_model=list[AdOut])
def get_ads(db: Session = Depends(get_db)):
    return db.query(Ad).all()

# 📋 Получение только своих объявлений
@router.get("/my", response_model=list[AdOut])
def read_my_ads(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    ads = db.query(Ad).filter(Ad.owner_id == current_user.id).all()
    return ads

# ✏️ Обновление объявления
@router.put("/{ad_id}", response_model=AdOut)
def update_ad(ad_id: int, ad_data: AdCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    ad = db.query(Ad).filter(Ad.id == ad_id).first()
    if not ad:
        raise HTTPException(status_code=404, detail="Объявление не найдено")
    if ad.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Вы не являетесь владельцем")
    ad.title = ad_data.title
    ad.description = ad_data.description
    ad.price = ad_data.price
    db.commit()
    db.refresh(ad)
    return ad

# ❌ Удаление объявления
@router.delete("/{ad_id}")
def delete_ad(ad_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    ad = db.query(Ad).filter(Ad.id == ad_id).first()
    if not ad:
        raise HTTPException(status_code=404, detail="Объявление не найдено")
    if ad.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Вы не являетесь владельцем")
    db.delete(ad)
    db.commit()
    return {"detail": "Объявление удалено"}
