from fastapi import FastAPI, Form, HTTPException
from passlib.context import CryptContext

app = FastAPI()

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Простое хранилище пользователей (в памяти)
users_db = {}


@app.post("/register")
def register(email: str = Form(...), password: str = Form(...)):
    if email in users_db:
        raise HTTPException(status_code=400, detail="Email уже зарегистрирован")
    hashed_password = pwd_context.hash(password)
    users_db[email] = hashed_password
    return {"message": "Регистрация успешна"}


@app.post("/login")
def login(email: str = Form(...), password: str = Form(...)):
    if email not in users_db:
        raise HTTPException(status_code=400, detail="Пользователь не найден")
    if not pwd_context.verify(password, users_db[email]):
        raise HTTPException(status_code=400, detail="Неверный пароль")
    return {"message": "Вход успешен"}
