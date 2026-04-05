from pydantic import BaseModel
from datetime import datetime


class BacktestRunResponse(BaseModel):
    id: str
    strategy_name: str
    start_ts: datetime
    end_ts: datetime
    pnl: float
    sharpe: float | None
    max_drawdown: float | None
    win_rate: float | None
    created_at: datetime