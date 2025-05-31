from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def root():
    return {"message": "P2P Exchange работает!"}

from auth import routes as auth_routes
app.include_router(auth_routes.router)
