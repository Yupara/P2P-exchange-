from pydantic import BaseModel

class UserCreate(BaseModel):
    username: str
    password: str

class UserOut(BaseModel):
    id: int
    username: str

    class Config:
        from_attributes = True  # ✅ FastAPI 2.x совместимость

class Token(BaseModel):
    access_token: str
    token_type: str
