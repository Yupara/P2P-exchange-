from pydantic import BaseModel

class AdBase(BaseModel):
    crypto: str
    fiat: str
    payment_method: str
    price: float
    type: str
    available: float

class AdCreate(AdBase):
    pass

class AdOut(AdBase):
    id: int

    class Config:
        # Здесь отступ 4 пробела, и это единственная строка внутри Config
        from_attributes = True
# schemas.py

from pydantic import BaseModel, EmailStr

class UserCreate(BaseModel):
    email: EmailStr
    password: str

class UserOut(BaseModel):
    id: int
    email: EmailStr

class Config:
    from_attributes = True     # для Pydantic v1
        # from_attributes = True  # если у вас Pydantic v2, вместо orm_mode
