from fastapi import FastAPI, HTTPException, Depends, APIRouter
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, EmailStr
from typing import List, Dict
from jose import jwt
from datetime import datetime, timedelta
from hashlib import sha256

# === Настройки ===
SECRET_KEY = "mysecret"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

app = FastAPI(title="P2P Exchange")

# === Схемы ===
class UserRegister(BaseModel):
    email: EmailStr
    password: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str

class AdCreate(BaseModel):
    title: str
    description: str
    price: float

class Ad(BaseModel):
    id: int
    title: str
    description: str
    price: float
    owner_id: int

# === Фейковая база ===
fake_users_db: Dict[str, dict] = {}
fake_user_id: Dict[str, int] = {}
fake_ads_db: Dict[int, Ad] = {}
next_ad_id = 1
user_counter = 1

# === Утилиты ===
def hash_password(password: str) -> str:
    return sha256(password.encode()).hexdigest()

def verify_password(input_password: str, user: dict) -> bool:
    return user["hashed_password"] == hash_password(input_password)

def create_access_token(data: dict, expires_delta: timedelta = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)):
    to_encode = data.copy()
    expire = datetime.utcnow() + expires_delta
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

bearer_scheme = HTTPBearer()

def verify_token(credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme)):
    token = credentials.credentials
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload.get("sub")
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid token")

# === Роуты ===
@app.post("/auth/register", tags=["auth"])
def register(user: UserRegister):
    global user_counter
    if user.email in fake_users_db:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    fake_users_db[user.email] = {
        "email": user.email,
        "hashed_password": hash_password(user.password)
    }
    fake_user_id[user.email] = user_counter
    user_counter += 1
    return {"message": "User registered successfully"}

@app.post("/auth/login", response_model=TokenResponse, tags=["auth"])
def login(user_data: UserLogin):
    user = fake_users_db.get(user_data.email)
    if not user or not verify_password(user_data.password, user):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    token = create_access_token({"sub": user_data.email})
    return {"access_token": token, "token_type": "bearer"}

@app.get("/auth/me", tags=["auth"])
def get_me(email: str = Depends(verify_token)):
    return {"email": email, "user_id": fake_user_id.get(email)}

# === Объявления ===
ads_router = APIRouter(prefix="/ads", tags=["ads"], dependencies=[Depends(verify_token)])

@ads_router.get("/", response_model=List[Ad])
def get_ads():
    return list(fake_ads_db.values())

@ads_router.post("/", response_model=Ad)
def create_ad(ad_data: AdCreate, email: str = Depends(verify_token)):
    global next_ad_id
    owner_id = fake_user_id.get(email)
    new_ad = Ad(id=next_ad_id, title=ad_data.title, description=ad_data.description, price=ad_data.price, owner_id=owner_id)
    fake_ads_db[next_ad_id] = new_ad
    next_ad_id += 1
    return new_ad

@ads_router.get("/my", response_model=List[Ad])
def my_ads(email: str = Depends(verify_token)):
    owner_id = fake_user_id.get(email)
    return [ad for ad in fake_ads_db.values() if ad.owner_id == owner_id]

# Регистрируем роутер
app.include_router(ads_router)

# Корень
@app.get("/")
def root():
    return {"message": "Welcome to P2P Exchange API"}
from fastapi import FastAPI
from auth.routes import router as auth_router
from ads_routes import router as ads_router  # 👈 новый импорт

app = FastAPI()

app.include_router(auth_router)
app.include_router(ads_router)  # 👈 подключаем ads
