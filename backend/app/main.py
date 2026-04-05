from fastapi import FastAPI
from app.api.routes import market, backtest

app = FastAPI(title="Trading System", version="0.1.0")

app.include_router(market.router, prefix="/market", tags=["market"])
app.include_router(backtest.router, prefix="/backtests", tags=["backtests"])


@app.get("/health")
def health():
    return {"status": "ok"}