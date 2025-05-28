from pydantic import BaseModel

class AdBase(BaseModel):
    crypto: str
    fiat: str
    payment_method: str
    price: float
    type: str
    available: float

class AdCreate(AdBase):
    pass

class AdOut(AdBase):
    id: int

    class Config:
        orm_mode = True
