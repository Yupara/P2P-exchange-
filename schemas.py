# ads/schemas.py
from pydantic import BaseModel
from typing import Optional

class AdBase(BaseModel):
    title: str
    description: Optional[str] = None
    price: float
    currency: str
    type: str  # buy or sell

class AdCreate(AdBase):
    pass

class AdUpdate(AdBase):
    pass

class AdOut(AdBase):
    id: int
    owner_id: int

    class Config:
        from_attributes = True
