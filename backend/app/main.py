from fastapi import FastAPI
from app.api.routes import market

app = FastAPI(title="Trading System", version="0.1.0")

app.include_router(market.router, prefix="/market", tags=["market"])


@app.get("/health")
def health():
    return {"status": "ok"}