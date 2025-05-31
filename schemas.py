from pydantic import BaseModel

class AdBase(BaseModel):
    title: str
    description: str
    price: float

class AdCreate(AdBase):
    pass

class AdOut(AdBase):
    id: int
    owner_id: int

    class Config:
        from_attributes = True
