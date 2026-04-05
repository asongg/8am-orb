from datetime import datetime

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.data.queries import get_bars
from app.db import get_db

router = APIRouter()


@router.get("/bars")
def read_bars(
    symbol: str = Query(...),
    start: datetime = Query(...),
    end: datetime = Query(...),
    timeframe: str = Query("1m"),
    limit: int = Query(5000, le=20000),
    db: Session = Depends(get_db),
):
    bars = get_bars(
        db=db,
        symbol=symbol,
        start=start,
        end=end,
        timeframe=timeframe,
        limit=limit,
    )

    return [
        {
            "symbol": b.symbol,
            "ts": b.ts.isoformat(),
            "timeframe": b.timeframe,
            "open": b.open,
            "high": b.high,
            "low": b.low,
            "close": b.close,
            "volume": b.volume,
        }
        for b in bars
    ]