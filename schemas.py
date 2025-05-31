from pydantic import BaseModel

class UserCreate(BaseModel):
    username: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

class AdCreate(BaseModel):
    title: str
    description: str
    price: float

class AdOut(AdCreate):
    id: int
    owner_id: int

    class Config:
        from_attributes = True  # Для Pydantic v2
