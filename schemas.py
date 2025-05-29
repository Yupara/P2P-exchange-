from pydantic import BaseModel, EmailStr


# ===== Входящие данные при регистрации и логине =====
class UserCreate(BaseModel):
    email: EmailStr
    password: str


# ===== Ответ клиенту (например, /me или /register) =====
class UserOut(BaseModel):
    id: int
    email: EmailStr

    class Config:
        from_attributes = True  # Если Pydantic v2
        # orm_mode = True       # Если Pydantic v1
