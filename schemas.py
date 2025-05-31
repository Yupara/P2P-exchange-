from pydantic import BaseModel, EmailStr
from typing import Optional

# Общие схемы для User
class UserCreate(BaseModel):
    email: EmailStr
    password: str

class UserOut(BaseModel):
    id: int
    email: EmailStr

    class Config:
        from_attributes = True  # Для Pydantic v2

# Схема токена
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None

# Общие схемы для Ad
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
