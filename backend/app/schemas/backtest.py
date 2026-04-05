from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class BacktestRunRequest(BaseModel):
    strategy_name: str = Field(..., examples=["opening_range_breakout"])
    symbol: str = Field(..., examples=["SPY"])
    start_ts: datetime
    end_ts: datetime
    params: dict[str, Any] = Field(default_factory=dict)


class BacktestRunResponse(BaseModel):
    id: str
    strategy_name: str
    params_json: dict[str, Any]
    start_ts: datetime
    end_ts: datetime
    pnl: float
    sharpe: float | None
    max_drawdown: float | None
    win_rate: float | None
    created_at: datetime


class BacktestRunDetailResponse(BacktestRunResponse):
    pass