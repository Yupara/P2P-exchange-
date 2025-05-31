# schemas.py

from pydantic import BaseModel, EmailStr
from typing import Optional

# --- User-схемы ---

class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str

class UserOut(BaseModel):
    id: int
    username: str
    email: EmailStr

    class Config:
        # В Pydantic v2 вместо orm_mode используется from_attributes
        from_attributes = True


# --- Token-схемы ---

class Token(BaseModel):
    access_token: str
    token_type: str


# --- Ad-схемы ---

class AdCreate(BaseModel):
    title: str
    description: str
    price: float

class AdOut(BaseModel):
    id: int
    title: str
    description: str
    price: float
    owner_id: int

    class Config:
        from_attributes = True
