from pydantic import BaseModel, EmailStr
from typing import Optional

# --- Схемы для User ---

class UserCreate(BaseModel):
    email: EmailStr
    password: str

class UserOut(BaseModel):
    id: int
    email: EmailStr

    class Config:
        from_attributes = True  # Pydantic v2: «использовать атрибуты модели»


# --- Схема токена JWT ---

class Token(BaseModel):
    access_token: str
    token_type: str


# --- Общие схемы для Ad ---

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
