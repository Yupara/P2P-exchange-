from pydantic import BaseModel, EmailStr
from typing import Optional

class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str

class UserOut(BaseModel):
    id: int
    username: str
    email: EmailStr

    class Config:
        orm_mode = True

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None

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
        orm_mode = True
