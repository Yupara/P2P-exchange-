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
        # Здесь отступ 4 пробела, и это единственная строка внутри Config
        from_attributes = True
