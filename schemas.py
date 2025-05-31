from pydantic import BaseModel

class UserOut(BaseModel):
    id: int
    username: str

    class Config:
        from_attributes = True  # заменяет orm_mode в Pydantic v2
