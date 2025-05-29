from pydantic import BaseModel, EmailStr
from typing import Optional


class UserCreate(BaseModel):
    email: EmailStr
    password: str


class UserOut(BaseModel):
    id: int
    email: EmailStr

    class Config:
        from_attributes = True


class AdCreate(BaseModel):
    title: str
    description: Optional[str] = None
    price: float


class AdOut(BaseModel):
    id: int
    title: str
    description: Optional[str]
    price: float
    owner_id: int

    class Config:
        from_attributes = True
