from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.orm import Session

from app.core.types import Bar
from app.models.bar import BarModel


def upsert_bars(db: Session, bars: list[Bar]) -> int:
    if not bars:
        return 0

    rows = [
        {
            "symbol": b.symbol,
            "ts": b.ts,
            "timeframe": b.timeframe,
            "open": b.open,
            "high": b.high,
            "low": b.low,
            "close": b.close,
            "volume": b.volume,
        }
        for b in bars
    ]

    stmt = insert(BarModel).values(rows)
    stmt = stmt.on_conflict_do_update(
        index_elements=["symbol", "ts", "timeframe"],
        set_={
            "open": stmt.excluded.open,
            "high": stmt.excluded.high,
            "low": stmt.excluded.low,
            "close": stmt.excluded.close,
            "volume": stmt.excluded.volume,
        },
    )

    result = db.execute(stmt)
    db.commit()
    return result.rowcount if result.rowcount is not None else len(rows)