from datetime import datetime, timedelta
import random
from zoneinfo import ZoneInfo

from app.core.types import Bar
from app.data.providers.base import MarketDataProvider


NY_TZ = ZoneInfo("America/New_York")
UTC = ZoneInfo("UTC")


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

        if start.tzinfo is None or end.tzinfo is None:
            raise ValueError("Start and end must be timezone-aware")

        bars: list[Bar] = []
        current_local = start.astimezone(NY_TZ)
        end_local = end.astimezone(NY_TZ)

        price = 100.0 + random.uniform(-5, 5)

        while current_local < end_local:
            if current_local.weekday() < 5:
                in_session = (
                    (current_local.hour > 9 or (current_local.hour == 9 and current_local.minute >= 30))
                    and current_local.hour < 16
                )

                if in_session:
                    drift = random.uniform(-0.25, 0.25)
                    open_px = price
                    close_px = max(1.0, open_px + drift)
                    high_px = max(open_px, close_px) + random.uniform(0, 0.15)
                    low_px = min(open_px, close_px) - random.uniform(0, 0.15)
                    volume = random.randint(100, 5000)

                    bars.append(
                        Bar(
                            symbol=symbol,
                            ts=current_local.astimezone(UTC),
                            open=round(open_px, 4),
                            high=round(high_px, 4),
                            low=round(low_px, 4),
                            close=round(close_px, 4),
                            volume=volume,
                            timeframe=timeframe,
                        )
                    )
                    price = close_px

            current_local += timedelta(minutes=1)

        return bars