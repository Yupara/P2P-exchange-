from datetime import timedelta

# Секретный ключ для подписи JWT (возьмите что-то сложное в реальной жизни)
SECRET_KEY = "supersecretkey123"

# Алгоритм подписи JWT
ALGORITHM = "HS256"

# Срок жизни токена (в минутах)
ACCESS_TOKEN_EXPIRE_MINUTES = 30
