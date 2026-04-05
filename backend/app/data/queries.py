from datetime import datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.bar import BarModel


def get_bars(
    db: Session,
    symbol: str,
    start: datetime,
    end: datetime,
    timeframe: str = "1m",
    limit: int = 5000,
):
    stmt = (
        select(BarModel)
        .where(BarModel.symbol == symbol)
        .where(BarModel.timeframe == timeframe)
        .where(BarModel.ts >= start)
        .where(BarModel.ts < end)
        .order_by(BarModel.ts.asc())
        .limit(limit)
    )

    return db.execute(stmt).scalars().all()