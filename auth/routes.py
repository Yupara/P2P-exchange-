from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import List
from auth.jwt_handler import verify_token

router = APIRouter(prefix="/ads", tags=["ads"])

# Временное хранилище в памяти
fake_ads_db = []
ad_id_counter = 1

class Ad(BaseModel):
    id: int
    title: str
    description: str
    price: float
    owner_email: str

class AdCreate(BaseModel):
    title: str
    description: str
    price: float

@router.post("/", response_model=Ad)
def create_ad(ad: AdCreate, email: str = Depends(verify_token)):
    global ad_id_counter
    new_ad = Ad(
        id=ad_id_counter,
        title=ad.title,
        description=ad.description,
        price=ad.price,
        owner_email=email
    )
    fake_ads_db.append(new_ad)
    ad_id_counter += 1
    return new_ad

@router.get("/", response_model=List[Ad])
def get_all_ads():
    return fake_ads_db

@router.get("/my", response_model=List[Ad])
def get_my_ads(email: str = Depends(verify_token)):
    return [ad for ad in fake_ads_db if ad.owner_email == email]

@router.put("/{ad_id}", response_model=Ad)
def update_ad(ad_id: int, ad: AdCreate, email: str = Depends(verify_token)):
    for existing_ad in fake_ads_db:
        if existing_ad.id == ad_id:
            if existing_ad.owner_email != email:
                raise HTTPException(status_code=403, detail="Forbidden")
            existing_ad.title = ad.title
            existing_ad.description = ad.description
            existing_ad.price = ad.price
            return existing_ad
    raise HTTPException(status_code=404, detail="Ad not found")

@router.delete("/{ad_id}")
def delete_ad(ad_id: int, email: str = Depends(verify_token)):
    for i, existing_ad in enumerate(fake_ads_db):
        if existing_ad.id == ad_id:
            if existing_ad.owner_email != email:
                raise HTTPException(status_code=403, detail="Forbidden")
            fake_ads_db.pop(i)
            return {"message": "Ad deleted"}
    raise HTTPException(status_code=404, detail="Ad not found")
