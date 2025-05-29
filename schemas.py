from pydantic import BaseModel
from typing import Optional

class UserOut(BaseModel):
    id: int
    email: str

    class Config:
        from_attributes = True


class AdBase(BaseModel):
    title: str
    description: str
    price: int


class AdCreate(AdBase):
    pass


class AdOut(AdBase):
    id: int
    owner_id: int

    class Config:
        from_attributes = True
