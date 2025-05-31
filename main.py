@app.post("/auth/login", response_model=TokenResponse, tags=["auth"])
def login(user_data: UserLogin):
    """
    Авторизация: сверяем пароль, возвращаем JWT токен.
    """
    user = fake_users_db.get(user_data.email)
    if not user or not verify_password(user_data.password, user):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    token = create_access_token({"sub": user_data.email})
    return {"access_token": token, "token_type": "bearer"}


@app.get("/auth/me", tags=["auth"])
def get_me(credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme)):
    """
    Проверка токена, возвращает email.
    """
    token = credentials.credentials
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email = payload.get("sub")
        if not email:
            raise HTTPException(status_code=401, detail="Invalid token")
        return {"email": email, "user_id": fake_user_id.get(email)}
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid token")
