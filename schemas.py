from pydantic import BaseModel, EmailStr


# ===== Входящие данные при регистрации и логине =====
class UserCreate(BaseModel):
    email: EmailStr
    password: str


# ===== Ответ клиенту (например, в /me или /register) =====
class UserOut(BaseModel):
    id: int
    email: EmailStr

    class Config:
        from_attributes = True  # если используешь Pydantic v2
        # orm_mode = True       # если Pydantic v1
        class UserOut(BaseModel):
    id: int
    email: EmailStr
    full_name: str  # ← если добавишь такое поле в модель

    class Config:
        from_attributes = True
