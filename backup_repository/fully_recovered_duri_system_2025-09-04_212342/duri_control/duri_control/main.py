from fastapi import FastAPI
from fastapi.responses import RedirectResponse
import os

app = FastAPI(title="DuRi Control API")

@app.get("/health")
def health():
    return {"status": "ok", "service": "duri_control"}

@app.get("/")
def root():
    # 루트로 오면 /docs 로 안내
    return RedirectResponse(url="/docs")
