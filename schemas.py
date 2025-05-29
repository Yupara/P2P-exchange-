from pydantic import BaseModel

class AdCreate(BaseModel):
    crypto: str
    fiat: str
    payment_method: str
    price: float
    type: str
    available: float

class AdOut(AdCreate):
    id: int

    class Config:
    from_attributes = True
