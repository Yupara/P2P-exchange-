from pydantic import BaseModel, EmailStr
from typing import Optional


# ----------- Пользователи -----------

class UserCreate(BaseModel):
    email: EmailStr
    password: str


class UserOut(BaseModel):
    id: int
    email: EmailStr

    class Config:
        orm_mode = True


# ----------- Токен -----------

class Token(BaseModel):
    access_token: str
    token_type: str


# ----------- Объявления -----------

class AdBase(BaseModel):
    title: str
    description: Optional[str] = None
    price: float
    currency: str
    payment_method: Optional[str] = None


class AdCreate(AdBase):
    pass


class AdOut(AdBase):
    id: int
    owner_id: int

    class Config:
        orm_mode = True
