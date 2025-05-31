from fastapi import FastAPI, APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from typing import List, Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from datetime import datetime, timedelta

# ――――――――― БАЗОВЫЕ НАСТРОЙКИ JWT ―――――――――
SECRET_KEY = "supersecretkey123"   # поменяйте на свою секретную строку (довольно длинную и случайную)
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60  # время жизни токена в минутах

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Функции для работы с JWT
def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    token = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return token

def verify_access_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate credentials")
        return email
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate credentials")


# ――――――――― МОДЕЛИ ДАННЫХ В ПАМЯТИ (имитация БД) ―――――――――

# Пользовательская модель
class User(BaseModel):
    id: int
    email: str
    hashed_password: str

# Схемы для входа/регистрации
class UserRegister(BaseModel):
    email: str
    password: str

class UserLogin(BaseModel):
    email: str
    password: str

class UserOut(BaseModel):
    id: int
    email: str

    class Config:
        orm_mode = True  # чтобы Pydantic мог возвращать объекты


# Объявление P2P
class Ad(BaseModel):
    id: int
    title: str
    description: str
    price: float
    owner_id: int

class AdCreate(BaseModel):
    title: str
    description: str
    price: float


# ――――――――― „База данных“ в оперативной памяти ―――――――――

# Словари для хранения: {email → User}, {id → Ad}
fake_users_db: dict[str, User] = {}
fake_ads_db: dict[int, Ad] = {}
next_user_id = 1
next_ad_id = 1


# ――――――――― ФУНКЦИИ И ЗАВИСИМОСТИ (Dependencies) ―――――――――

def get_current_user(token: str = Depends(lambda: "")):
    """
    Dependency, которая получает токен из заголовка Authorization:
      Authorization: Bearer <token>
    и возвращает объект User, если токен валиден, или кидает HTTPException.
    """
    # Получаем "Authorization" заголовок вручную
    from fastapi import Request
    request = Request.scope.get("request_scope")  # не реально, оставим для примера
    # Но проще — привяжем функцию ниже, см. пример в route-ах
    raise NotImplementedError("Этот метод заменяется в route-ах")


# Но фактически мы не сможем вычитать токен через Depends(lambda: ""),
# поэтому подключим BearerToken-зависимость в каждом route.


# ――――――――― НАСТРОИМ FastAPI И РОУТЕРЫ ―――――――――

app = FastAPI()

# Роутер для авторизации
auth_router = APIRouter(prefix="/auth", tags=["auth"])


@auth_router.post("/register", response_model=UserOut)
def register(user_data: UserRegister):
    global next_user_id
    if user_data.email in fake_users_db:
        raise HTTPException(status_code=400, detail="Email already registered")
    hashed = pwd_context.hash(user_data.password)
    user = User(id=next_user_id, email=user_data.email, hashed_password=hashed)
    fake_users_db[user_data.email] = user
    next_user_id += 1
    return user

@auth_router.post("/login")
def login(user_data: UserLogin):
    # Проверим, что пользователь есть
    user = fake_users_db.get(user_data.email)
    if not user or not pwd_context.verify(user_data.password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    # Создаём токен
    access_token = create_access_token({"sub": user.email})
    return {"access_token": access_token, "token_type": "bearer"}

@auth_router.get("/me", response_model=UserOut)
def read_users_me(authorization: Optional[str] = None):
    """
    GET /auth/me
    В заголовке: Authorization: Bearer <token>
    """
    if not authorization:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")
    parts = authorization.split()
    if len(parts) != 2 or parts[0].lower() != "bearer":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")
    token = parts[1]
    email = verify_access_token(token)
    user = fake_users_db.get(email)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return user


# Роутер для объявлений
ads_router = APIRouter(prefix="/ads", tags=["ads"])


def get_user_from_header(authorization: Optional[str] = None) -> User:
    """
    Заменяет зависимость get_current_user
    Парсит токен из Authorization и возвращает User из fake_users_db
    """
    if not authorization:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")
    parts = authorization.split()
    if len(parts) != 2 or parts[0].lower() != "bearer":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")
    token = parts[1]
    email = verify_access_token(token)
    user = fake_users_db.get(email)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return user


@ads_router.get("/", response_model=List[Ad])
def get_ads():
    """
    GET /ads/  — посмотреть все объявления
    """
    return list(fake_ads_db.values())


@ads_router.get("/my", response_model=List[Ad])
def get_my_ads(authorization: Optional[str] = None):
    """
    GET /ads/my  — посмотреть только свои объявления
    """
    user = get_user_from_header(authorization)
    result = [ad for ad in fake_ads_db.values() if ad.owner_id == user.id]
    return result


@ads_router.post("/", response_model=Ad)
def create_ad(ad_data: AdCreate, authorization: Optional[str] = None):
    """
    POST /ads/  — создает новое объявление от текущего пользователя
    Body: { title, description, price }
    """
    global next_ad_id
    user = get_user_from_header(authorization)
    ad = Ad(
        id=next_ad_id,
        title=ad_data.title,
        description=ad_data.description,
        price=ad_data.price,
        owner_id=user.id
    )
    fake_ads_db[next_ad_id] = ad
    next_ad_id += 1
    return ad


@ads_router.put("/{ad_id}", response_model=Ad)
def update_ad(ad_id: int, ad_data: AdCreate, authorization: Optional[str] = None):
    """
    PUT /ads/{ad_id}  — редактировать своё объявление
    """
    user = get_user_from_header(authorization)
    ad = fake_ads_db.get(ad_id)
    if not ad:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Ad not found")
    if ad.owner_id != user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")
    ad.title = ad_data.title
    ad.description = ad_data.description
    ad.price = ad_data.price
    fake_ads_db[ad_id] = ad
    return ad


@ads_router.delete("/{ad_id}")
def delete_ad(ad_id: int, authorization: Optional[str] = None):
    """
    DELETE /ads/{ad_id}  — удалить своё объявление
    """
    user = get_user_from_header(authorization)
    ad = fake_ads_db.get(ad_id)
    if not ad:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Ad not found")
    if ad.owner_id != user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")
    del fake_ads_db[ad_id]
    return {"message": "Ad deleted"}


# Подключаем роутеры в приложении
app.include_router(auth_router)
app.include_router(ads_router)
