from abc import ABC, abstractmethod
from datetime import datetime

from app.core.types import Bar


class MarketDataProvider(ABC):
    @abstractmethod
    def fetch_bars(
        self,
        symbol: str,
        start: datetime,
        end: datetime,
        timeframe: str = "1m",
    ) -> list[Bar]:
        raise NotImplementedError