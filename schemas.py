from pydantic import BaseModel
from typing import Optional

# Модель для возвращаемого пользователя (при регистрации, /me и т.д.)
class UserOut(BaseModel):
    id: int
    email: str

    class Config:
        from_attributes = True  # Для Pydantic v2

# Остальное — объявления (если уже добавил ранее)
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
from pydantic import BaseModel

class AdCreate(BaseModel):
    title: str
    description: str
    price: float
