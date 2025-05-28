from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from .. import schemas, models, database

router = APIRouter()

@router.post("/ads", response_model=schemas.AdOut)
def create_ad(ad: schemas.AdCreate, db: Session = Depends(database.get_db)):
    db_ad = models.Advertisement(**ad.dict())
    db.add(db_ad)
    db.commit()
    db.refresh(db_ad)
    return db_ad

@router.get("/ads", response_model=list[schemas.AdOut])
def list_ads(
    crypto: str = Query(None),
    fiat: str = Query(None),
    payment_method: str = Query(None),
    type: str = Query(None),
    db: Session = Depends(database.get_db)
):
    query = db.query(models.Advertisement)
    if crypto:
        query = query.filter(models.Advertisement.crypto == crypto)
    if fiat:
        query = query.filter(models.Advertisement.fiat == fiat)
    if payment_method:
        query = query.filter(models.Advertisement.payment_method == payment_method)
    if type:
        query = query.filter(models.Advertisement.type == type)
    return query.all()
