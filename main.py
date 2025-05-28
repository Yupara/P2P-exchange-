from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel
from typing import List, Optional

app = FastAPI()

class Ad(BaseModel):
    id: int
    crypto: str
    fiat: str
    payment_method: str
    price: float
    type: str  # buy / sell
    available: float

ads_db = []

@app.post("/create_ad")
def create_ad(ad: Ad):
    ads_db.append(ad)
    return {"message": "Объявление создано", "ad": ad}

@app.get("/search_ads")
def search_ads(
    crypto: Optional[str] = Query(None),
    fiat: Optional[str] = Query(None),
    payment_method: Optional[str] = Query(None),
    type: Optional[str] = Query(None)
):
    results = ads_db
    if crypto:
        results = [ad for ad in results if ad.crypto == crypto]
    if fiat:
        results = [ad for ad in results if ad.fiat == fiat]
    if payment_method:
        results = [ad for ad in results if ad.payment_method == payment_method]
    if type:
        results = [ad for ad in results if ad.type == type]
    return {"results": results}
