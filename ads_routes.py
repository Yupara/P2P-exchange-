from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from auth.deps import get_db, get_current_user
from models import Ad, User
from schemas import AdCreate, AdOut

router = APIRouter()

@router.post("/", response_model=AdOut)
def create_ad(ad: AdCreate, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    db_ad = Ad(**ad.dict(), owner_id=user.id)
    db.add(db_ad)
    db.commit()
    db.refresh(db_ad)
    return db_ad

@router.get("/", response_model=list[AdOut])
def list_ads(db: Session = Depends(get_db)):
    return db.query(Ad).all()

@router.get("/my", response_model=list[AdOut])
def list_my_ads(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return db.query(Ad).filter(Ad.owner_id == user.id).all()
