from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from auth.deps import get_db, get_current_user
from schemas import AdCreate, AdOut
from models import Ad, User

router = APIRouter()

@router.post("/", response_model=AdOut)
def create_ad(ad_data: AdCreate, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    ad = Ad(**ad_data.dict(), owner_id=user.id)
    db.add(ad)
    db.commit()
    db.refresh(ad)
    return ad

@router.get("/", response_model=list[AdOut])
def get_ads(db: Session = Depends(get_db)):
    return db.query(Ad).all()

@router.get("/my", response_model=list[AdOut])
def get_my_ads(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return db.query(Ad).filter(Ad.owner_id == user.id).all()

@router.put("/{ad_id}", response_model=AdOut)
def update_ad(ad_id: int, ad_data: AdCreate, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    ad = db.query(Ad).filter(Ad.id == ad_id).first()
    if not ad or ad.owner_id != user.id:
        raise HTTPException(status_code=403, detail="Not authorized")
    for field, value in ad_data.dict().items():
        setattr(ad, field, value)
    db.commit()
    db.refresh(ad)
    return ad

@router.delete("/{ad_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_ad(ad_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    ad = db.query(Ad).filter(Ad.id == ad_id).first()
    if not ad or ad.owner_id != user.id:
        raise HTTPException(status_code=403, detail="Not authorized")
    db.delete(ad)
    db.commit()
