from fastapi.security import OAuth2PasswordBearer

# 🔥 ВАЖНО: БЕЗ начального слэша — иначе Swagger НЕ покажет Authorize
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")
