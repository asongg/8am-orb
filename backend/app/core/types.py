from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

@dataclass
class Bar:
    symbol: str
    ts: datetime
    open: float
    high: float
    low: float
    close: float
    volume: int
    timeframe: str = "1m"

@dataclass
class Signal:
    strategy_name: str
    symbol: str
    ts: datetime
    side: str
    strength: float | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

@dataclass
class OrderRequest:
    strategy_name: str
    symbol: str
    side: str
    qty: float
    order_type: str = "MARKET"
    limit_price: float | None = None