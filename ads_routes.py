# ads_routes.py

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from auth.deps import get_current_user
from database import get_db
from models import Ad, User
from schemas import AdCreate, AdOut

router = APIRouter(
    prefix="/ads",
    tags=["ads"],
)

@router.post("/", response_model=AdOut, status_code=status.HTTP_201_CREATED)
def create_ad(
    ad_data: AdCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Создание объявления. Владелец — текущий пользователь.
    """
    db_ad = Ad(**ad_data.dict(), owner_id=current_user.id)
    db.add(db_ad)
    db.commit()
    db.refresh(db_ad)
    return db_ad

@router.get("/", response_model=list[AdOut])
def list_ads(db: Session = Depends(get_db)):
    """
    Просмотр всех объявлений (публично доступно).
    """
    return db.query(Ad).all()

@router.get("/my", response_model=list[AdOut])
def list_my_ads(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Просмотр объявлений текущего пользователя.
    """
    return db.query(Ad).filter(Ad.owner_id == current_user.id).all()
