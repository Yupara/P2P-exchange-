# main.py

from fastapi import FastAPI, Depends, HTTPException, status, APIRouter
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel, EmailStr
from typing import List
from sqlalchemy import Column, Integer, String, Float, ForeignKey, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship, Session
from passlib.context import CryptContext
from jose import jwt, JWTError
from datetime import datetime, timedelta

### === 1. Настройка конфигурации (секретный ключ, алгоритм, время жизни) ===

SECRET_KEY = "replace_with_your_own_secret_key"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

### === 2. Настройка базы данных (SQLite, файл test.db в той же папке) ===

SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    """
    Зависимость, создаёт сессию и закрывает её после каждого запроса.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

### === 3. Cловарь для работы с паролями (bcrypt) ===

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

### === 4. Модели SQLAlchemy ===

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)

    ads = relationship("Ad", back_populates="owner")


class Ad(Base):
    __tablename__ = "ads"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(String, nullable=False)
    price = Column(Float, nullable=False)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    owner = relationship("User", back_populates="ads")


# Создаём таблицы (если их ещё нет)
Base.metadata.create_all(bind=engine)

### === 5. Pydantic-схемы ===

class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str

class UserOut(BaseModel):
    id: int
    username: str
    email: EmailStr

    class Config:
        from_attributes = True  # для Pydantic v2 (раньше orm_mode=True)

class Token(BaseModel):
    access_token: str
    token_type: str

class AdCreate(BaseModel):
    title: str
    description: str
    price: float

class AdOut(BaseModel):
    id: int
    title: str
    description: str
    price: float
    owner_id: int

    class Config:
        from_attributes = True

### === 6. Функции для JWT ===

def create_access_token(data: dict) -> str:
    """
    Генерирует JWT с полем "sub": user_id и временем жизни.
    """
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def decode_access_token(token: str) -> dict:
    """
    Декодирует JWT, возвращает payload или бросает JWTError.
    """
    return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])

### === 7. Зависимость для полученного пользователем по токену ===

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = decode_access_token(token)
        user_id: int = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    user = db.query(User).filter(User.id == int(user_id)).first()
    if user is None:
        raise credentials_exception
    return user

### === 8. Сервисы работы с юзером ===

def get_user_by_username(db: Session, username: str) -> User | None:
    return db.query(User).filter(User.username == username).first()

def get_user_by_email(db: Session, email: str) -> User | None:
    return db.query(User).filter(User.email == email).first()

def create_user(db: Session, username: str, email: str, password: str) -> User:
    hashed = hash_password(password)
    user = User(username=username, email=email, hashed_password=hashed)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

def authenticate_user(db: Session, username_or_email: str, password: str) -> User | None:
    user = db.query(User).filter(User.username == username_or_email).first()
    if not user:
        user = db.query(User).filter(User.email == username_or_email).first()
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user

### === 9. Роуты для аутентификации ===

auth_router = APIRouter(prefix="/auth", tags=["auth"])

@auth_router.post("/register", response_model=UserOut, status_code=status.HTTP_201_CREATED)
def register(user_data: UserCreate, db: Session = Depends(get_db)):
    # Проверяем уникальность username и email
    if get_user_by_username(db, user_data.username):
        raise HTTPException(status_code=400, detail="Username already registered")
    if get_user_by_email(db, user_data.email):
        raise HTTPException(status_code=400, detail="Email already registered")
    new_user = create_user(db, username=user_data.username, email=user_data.email, password=user_data.password)
    return new_user

@auth_router.post("/login", response_model=Token)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    # form_data.username может быть либо username, либо email
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    # Создаём JWT
    token = create_access_token(data={"sub": str(user.id)})
    return {"access_token": token, "token_type": "bearer"}

@auth_router.get("/me", response_model=UserOut)
def read_current_user(current_user: User = Depends(get_current_user)):
    """
    GET /auth/me — возвращает информацию о текущем авторизованном пользователе.
    """
    return current_user

### === 10. Роуты для объявлений ===

ads_router = APIRouter(prefix="/ads", tags=["ads"])

@ads_router.post("/", response_model=AdOut, status_code=status.HTTP_201_CREATED)
def create_ad(
    ad_data: AdCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Создание объявления — доступно только авторизованным.
    """
    db_ad = Ad(**ad_data.dict(), owner_id=current_user.id)
    db.add(db_ad)
    db.commit()
    db.refresh(db_ad)
    return db_ad

@ads_router.get("/", response_model=List[AdOut])
def list_ads(db: Session = Depends(get_db)):
    """
    GET /ads/ — возвращает все объявления (публично).
    """
    return db.query(Ad).all()

@ads_router.get("/my", response_model=List[AdOut])
def list_my_ads(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    GET /ads/my — возвращает объявления текущего (авторизованного) пользователя.
    """
    return db.query(Ad).filter(Ad.owner_id == current_user.id).all()

### === 11. Инициализируем приложение и подключаем роуты ===

app = FastAPI(title="P2P Exchange API")

app.include_router(auth_router)
app.include_router(ads_router)

@app.get("/", tags=["root"])
def read_root():
    return {"message": "P2P Exchange API работает!"}
