from pydantic import BaseModel

# Пользователь (только для ответа)
class UserOut(BaseModel):
    id: int
    email: str

    class Config:
        from_attributes = True

# Объявление - создание
class AdCreate(BaseModel):
    currency: str
    amount: float
    ad_type: str  # buy / sell

# Объявление - ответ
class AdOut(BaseModel):
    id: int
    currency: str
    amount: float
    ad_type: str
    owner_id: int

    class Config:
        from_attributes = True
