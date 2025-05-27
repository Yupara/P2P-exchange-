from fastapi import FastAPI

app = FastAPI()


@app.get("/")
def home():
    return {"message": "P2P-обменник работает"}
