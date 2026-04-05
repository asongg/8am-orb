from datetime import datetime, timedelta, timezone

from app.db import SessionLocal
from app.data.ingestion import upsert_bars
from app.data.providers.mock_data import MockMarketDataProvider


def main():
    provider = MockMarketDataProvider()

    end = datetime.now(timezone.utc).replace(second=0, microsecond=0)
    start = end - timedelta(days=5)

    symbols = ["SPY", "QQQ", "AAPL", "MSFT", "NVDA"]

    with SessionLocal() as db:
        total = 0
        for symbol in symbols:
            bars = provider.fetch_bars(symbol=symbol, start=start, end=end, timeframe="1m")
            inserted = upsert_bars(db, bars)
            total += inserted
            print(f"{symbol}: upserted {inserted} bars")

    print(f"Done. Total bars processed: {total}")


if __name__ == "__main__":
    main()