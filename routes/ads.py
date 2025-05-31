# routes/routes/ads.py

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from typing import List

# Импортируем verify_token из main.py (root)
from main import verify_token  

#
#  Pydantic-модели для объявлений
#
class Ad(BaseModel):
    id: int
    title: str
    description: str
    price: float
    owner_id: int

class AdCreate(BaseModel):
    title: str
    description: str
    price: float

#
# «База» объявлений в памяти (id -> Ad)
#
fake_ads_db: dict[int, Ad] = {}
next_ad_id = 1

#
# Настраиваем APIRouter: все эндпоинты /ads/* требуют валидный Bearer-токен
#
router = APIRouter(
    prefix="/ads",
    tags=["ads"],
    dependencies=[Depends(verify_token)]
)

@router.get("/", response_model=List[Ad], summary="Get all ads")
def get_ads():
    """
    GET /ads/  — возвращает список всех объявлений.
    (Требуется JWT, потому что dependencies=[Depends(verify_token)].)
    """
    return list(fake_ads_db.values())

@router.get("/my", response_model=List[Ad], summary="Get my ads")
def get_my_ads(email: str = Depends(verify_token)):
    """
    GET /ads/my — возвращает только те объявления,
    у которых owner_id == hash(email) % 1000.
    """
    owner_id = hash(email) % 1000
    return [ad for ad in fake_ads_db.values() if ad.owner_id == owner_id]

@router.post("/", response_model=Ad, summary="Create ad")
def create_ad(
    ad_data: AdCreate,
    email: str = Depends(verify_token)
):
    """
    POST /ads/ — создаёт новое объявление.  
    owner_id = hash(email) % 1000.
    """
    global next_ad_id
    owner_id = hash(email) % 1000
    new_ad = Ad(
        id=next_ad_id,
        title=ad_data.title,
        description=ad_data.description,
        price=ad_data.price,
        owner_id=owner_id
    )
    fake_ads_db[next_ad_id] = new_ad
    next_ad_id += 1
    return new_ad

@router.put("/{ad_id}", response_model=Ad, summary="Update ad")
def update_ad(
    ad_id: int,
    ad_data: AdCreate,
    email: str = Depends(verify_token)
):
    """
    PUT /ads/{ad_id} — обновляет объявление.  
    Только условие: ad.owner_id == hash(email)%1000, иначе 403.
    """
    ad = fake_ads_db.get(ad_id)
    if not ad:
        raise HTTPException(status_code=404, detail="Ad not found")
    if ad.owner_id != (hash(email) % 1000):
        raise HTTPException(status_code=403, detail="Not authorized")
    ad.title = ad_data.title
    ad.description = ad_data.description
    ad.price = ad_data.price
    fake_ads_db[ad_id] = ad
    return ad

@router.delete("/{ad_id}", summary="Delete ad")
def delete_ad(
    ad_id: int,
    email: str = Depends(verify_token)
):
    """
    DELETE /ads/{ad_id} — удаляет объявление,
    если ad.owner_id == hash(email)%1000, иначе 403.
    """
    ad = fake_ads_db.get(ad_id)
    if not ad:
        raise HTTPException(status_code=404, detail="Ad not found")
    if ad.owner_id != (hash(email) % 1000):
        raise HTTPException(status_code=403, detail="Not authorized")
    del fake_ads_db[ad_id]
    return {"message": "Ad deleted"}
