# main.py

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# 1) Роутер авторизации (из пакета auth)
from auth.routes import router as auth_router

# 2) Роутер объявлений
# У нас ads.py лежит в routes/routes/ads.py, поэтому импорт такой:
from routes.routes.ads import router as ads_router

# 3) Запуск FastAPI
app = FastAPI(title="P2P Exchange API")

# Если вам нужен CORS (например, для фронтенда):
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],            
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 4) Подключаем роутеры
app.include_router(auth_router, prefix="/auth", tags=["auth"])
app.include_router(ads_router, prefix="/ads", tags=["ads"])

# 5) “Заглушка” корневого эндпоинта (опционально)
@app.get("/", summary="Root endpoint")
def root():
    return {"message": "Welcome to P2P Exchange API"}
