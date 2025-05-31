# schemas.py

from pydantic import BaseModel

class UserCreate(BaseModel):
    username: str
    password: str

class UserOut(BaseModel):
    id: int
    username: str

    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str

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
