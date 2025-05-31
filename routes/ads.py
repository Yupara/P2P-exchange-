from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from typing import List

# Импортируем verify_token (функцию проверки JWT) из main.py
from main import verify_token

# ---------------------------------------------------
# 1. Pydantic-модели для объявлений
# ---------------------------------------------------
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

# ---------------------------------------------------
# 2. Эмуляция “базы” объявлений в памяти (id → Ad)
# ---------------------------------------------------
fake_ads_db: dict[int, Ad] = {}
next_ad_id = 1

# ---------------------------------------------------
# 3. Роутер /ads (все маршруты /ads/* защищены JWT)
# ---------------------------------------------------
router = APIRouter(
    prefix="/ads",
    tags=["ads"],
    dependencies=[Depends(verify_token)]  # **ВСЁ** в этом роутере требует валидный JWT
)

@router.get("/", response_model=List[Ad], summary="Get all ads")
def get_ads():
    """
    GET /ads/
    Вернёт список всех объявлений.  
    (Так как dependencies=[Depends(verify_token)], нужен Bearer-токен.)
    """
    return list(fake_ads_db.values())

@router.get("/my", response_model=List[Ad], summary="Get my ads")
def get_my_ads(email: str = Depends(verify_token)):
    """
    GET /ads/my
    Вернёт только объявления, owner_id которых = hash(email)%1000.
    """
    owner_id = hash(email) % 1000
    return [ad for ad in fake_ads_db.values() if ad.owner_id == owner_id]

@router.post("/", response_model=Ad, summary="Create ad")
def create_ad(
    ad_data: AdCreate,
    email: str = Depends(verify_token)
):
    """
    POST /ads/
    Body (JSON): { "title": "...", "description": "...", "price": ... }
    Создаёт новое объявление и возвращает его.  
    owner_id = hash(email)%1000 (эмуляция ID текущего пользователя).
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
    PUT /ads/{ad_id}
    Позволяет обновить объявление только его владельцу.  
    Если ad_id не найден → 404.  
    Если owner_id != hash(email)%1000 → 403.
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
    DELETE /ads/{ad_id}
    Удаляет объявление только его владельцу.  
    Если ad_id не найден → 404.  
    Если owner_id != hash(email)%1000 → 403.
    """
    ad = fake_ads_db.get(ad_id)
    if not ad:
        raise HTTPException(status_code=404, detail="Ad not found")
    if ad.owner_id != (hash(email) % 1000):
        raise HTTPException(status_code=403, detail="Not authorized")
    del fake_ads_db[ad_id]
    return {"message": "Ad deleted"}
