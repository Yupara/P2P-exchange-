from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from auth.deps import get_db, get_current_user
from schemas import AdCreate, AdOut
from models import Ad, User

router = APIRouter(prefix="/ads", tags=["ads"])

@router.post("/", response_model=AdOut)
def create_ad(ad: AdCreate, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    db_ad = Ad(**ad.dict(), owner_id=user.id)
    db.add(db_ad)
    db.commit()
    db.refresh(db_ad)
    return db_ad

@router.get("/", response_model=list[AdOut])
def get_ads(db: Session = Depends(get_db)):
    return db.query(Ad).all()

@router.get("/my", response_model=list[AdOut])
def get_my_ads(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return db.query(Ad).filter(Ad.owner_id == user.id).all()

@router.put("/{ad_id}", response_model=AdOut)
def update_ad(ad_id: int, new_ad: AdCreate, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    ad = db.query(Ad).filter(Ad.id == ad_id).first()
    if not ad:
        raise HTTPException(status_code=404, detail="Not found")
    if ad.owner_id != user.id:
        raise HTTPException(status_code=403, detail="Not allowed")
    for field, value in new_ad.dict().items():
        setattr(ad, field, value)
    db.commit()
    db.refresh(ad)
    return ad

@router.delete("/{ad_id}")
def delete_ad(ad_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    ad = db.query(Ad).filter(Ad.id == ad_id).first()
    if not ad:
        raise HTTPException(status_code=404, detail="Not found")
    if ad.owner_id != user.id:
        raise HTTPException(status_code=403, detail="Not allowed")
    db.delete(ad)
    db.commit()
    return {"detail": "Ad deleted"}
