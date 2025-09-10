#!/usr/bin/env python3
"""
간단한 DuRi Control API 서버
"""

from fastapi import FastAPI
from fastapi.responses import RedirectResponse, JSONResponse
from datetime import datetime

app = FastAPI(docs_url="/docs", redoc_url=None, redirect_slashes=False)

@app.get("/health", include_in_schema=False)
def health():
    return JSONResponse({
        "status": "ok",
        "service": "duri_control",
        "timestamp": datetime.now().isoformat()
    })

@app.get("/", include_in_schema=False)
def root():
    return RedirectResponse("/docs")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8083)
