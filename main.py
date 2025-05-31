from fastapi import FastAPI
from auth.routes import router as auth_router
from ads_routes import router as ads_router

app = FastAPI(title="P2P Exchange API")

# Регистрируем роуты
app.include_router(auth_router, prefix="/auth", tags=["auth"])
app.include_router(ads_router, prefix="/ads", tags=["ads"])

@app.get("/", tags=["Root"])
def root():
    return {"message": "P2P Exchange API работает"}
