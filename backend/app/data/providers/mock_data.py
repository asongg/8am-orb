from datetime import datetime, timedelta, timezone
import random

from app.core.types import Bar
from app.data.providers.base import MarketDataProvider


class MockMarketDataProvider(MarketDataProvider):
    def fetch_bars(
        self,
        symbol: str,
        start: datetime,
        end: datetime,
        timeframe: str = "1m",
    ) -> list[Bar]:
        if timeframe != "1m":
            raise ValueError("Mock provider currently only supports 1m timeframe")

        bars: list[Bar] = []
        current = start
        price = 100.0 + random.uniform(-5, 5)

        while current < end:
            if current.weekday() < 5:
                if (
                    (current.hour > 9 or (current.hour == 9 and current.minute >= 30))
                    and current.hour < 16
                ):
                    drift = random.uniform(-0.25, 0.25)
                    open_px = price
                    close_px = max(1.0, open_px + drift)
                    high_px = max(open_px, close_px) + random.uniform(0, 0.15)
                    low_px = min(open_px, close_px) - random.uniform(0, 0.15)
                    volume = random.randint(100, 5000)

                    bars.append(
                        Bar(
                            symbol=symbol,
                            ts=current,
                            open=round(open_px, 4),
                            high=round(high_px, 4),
                            low=round(low_px, 4),
                            close=round(close_px, 4),
                            volume=volume,
                            timeframe=timeframe,
                        )
                    )
                    price = close_px

            current += timedelta(minutes=1)

        return bars