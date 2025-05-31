from fastapi import FastAPI, APIRouter, Depends
from typing import List
from pydantic import BaseModel

app = FastAPI()

# 1) Определяем схемы (Pydantic-модели)
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

# 2) Эмуляция “базы” в памяти
fake_ads_db: dict[int, Ad] = {}
next_ad_id = 1

# 3) Создаём роутер и сразу в нём указываем: 
#    любой маршрут в этом роутере требует verify_token → Bearer 
ads_router = APIRouter(
    prefix="/ads",
    tags=["ads"],
    dependencies=[Depends(verify_token)]  # вот здесь
)

@ads_router.get("/", response_model=List[Ad], summary="Get all ads")
def get_ads():
    return list(fake_ads_db.values())

@ads_router.post("/", response_model=Ad, summary="Create ad")
def create_ad(
    ad_data: AdCreate,
    email: str = Depends(verify_token)  # можно повторно вызывать, но router.dependencies уже проверил токен
):
    global next_ad_id
    # в JWT в поле "sub" мы храним email пользователя
    # для примера owner_id = хеш(email) % 1000  (либо возьмите ID из вашей БД)
    owner_id = hash(email) % 1000
    new_ad = Ad(id=next_ad_id, title=ad_data.title, description=ad_data.description, price=ad_data.price, owner_id=owner_id)
    fake_ads_db[next_ad_id] = new_ad
    next_ad_id += 1
    return new_ad

@ads_router.put("/{ad_id}", response_model=Ad, summary="Update ad")
def update_ad(
    ad_id: int,
    ad_data: AdCreate,
    email: str = Depends(verify_token)
):
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

@ads_router.delete("/{ad_id}", summary="Delete ad")
def delete_ad(
    ad_id: int,
    email: str = Depends(verify_token)
):
    ad = fake_ads_db.get(ad_id)
    if not ad:
        raise HTTPException(status_code=404, detail="Ad not found")
    if ad.owner_id != (hash(email) % 1000):
        raise HTTPException(status_code=403, detail="Not authorized")
    del fake_ads_db[ad_id]
    return {"message": "Ad deleted"}

# Регистрируем роутер
app.include_router(ads_router)

# Простой публичный маршрут, чтобы проверить, что сервер жив
@app.get("/", summary="Root endpoint")
def root():
    return {"message": "Welcome to P2P Exchange API"}
