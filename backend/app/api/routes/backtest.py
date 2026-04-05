from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db import get_db
from app.models.backtest_run import BacktestRunModel

router = APIRouter()


@router.get("")
def list_backtests(db: Session = Depends(get_db)):
    stmt = select(BacktestRunModel).order_by(BacktestRunModel.created_at.desc())
    runs = db.execute(stmt).scalars().all()

    return [
        {
            "id": str(r.id),
            "strategy_name": r.strategy_name,
            "params_json": r.params_json,
            "start_ts": r.start_ts.isoformat(),
            "end_ts": r.end_ts.isoformat(),
            "pnl": r.pnl,
            "sharpe": r.sharpe,
            "max_drawdown": r.max_drawdown,
            "win_rate": r.win_rate,
            "created_at": r.created_at.isoformat(),
        }
        for r in runs
    ]