from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db import get_db
from app.schemas.backtest import (
    BacktestRunDetailResponse,
    BacktestRunRequest,
    BacktestRunResponse,
)
from app.services.backtest_service import (
    get_backtest_run,
    list_backtest_runs,
    list_backtest_trades,
    list_equity_snapshots,
    run_backtest_and_persist,
)

router = APIRouter()


def serialize_run(r) -> dict:
    return {
        "id": str(r.id),
        "strategy_name": r.strategy_name,
        "params_json": r.params_json,
        "start_ts": r.start_ts,
        "end_ts": r.end_ts,
        "pnl": r.pnl,
        "sharpe": r.sharpe,
        "max_drawdown": r.max_drawdown,
        "win_rate": r.win_rate,
        "created_at": r.created_at,
    }


@router.get("", response_model=list[BacktestRunResponse])
def list_backtests(db: Session = Depends(get_db)):
    runs = list_backtest_runs(db)
    return [serialize_run(r) for r in runs]


@router.get("/{run_id}", response_model=BacktestRunDetailResponse)
def get_backtest(run_id: str, db: Session = Depends(get_db)):
    run = get_backtest_run(db, run_id)
    if not run:
        raise HTTPException(status_code=404, detail="Backtest run not found")
    return serialize_run(run)


@router.get("/{run_id}/trades")
def get_backtest_trades(run_id: str, db: Session = Depends(get_db)):
    run = get_backtest_run(db, run_id)
    if not run:
        raise HTTPException(status_code=404, detail="Backtest run not found")

    trades = list_backtest_trades(db, run_id)
    return [
        {
            "id": str(t.id),
            "backtest_run_id": str(t.backtest_run_id),
            "symbol": t.symbol,
            "side": t.side,
            "qty": t.qty,
            "fill_price": t.fill_price,
            "fill_ts": t.fill_ts.isoformat(),
            "trade_index": t.trade_index,
        }
        for t in trades
    ]


@router.get("/{run_id}/equity")
def get_backtest_equity(run_id: str, db: Session = Depends(get_db)):
    run = get_backtest_run(db, run_id)
    if not run:
        raise HTTPException(status_code=404, detail="Backtest run not found")

    snapshots = list_equity_snapshots(db, run_id)
    return [
        {
            "id": str(s.id),
            "backtest_run_id": str(s.backtest_run_id),
            "ts": s.ts.isoformat(),
            "equity": s.equity,
            "snapshot_index": s.snapshot_index,
        }
        for s in snapshots
    ]


@router.post("/run", response_model=BacktestRunResponse)
def run_backtest(request: BacktestRunRequest, db: Session = Depends(get_db)):
    try:
        run = run_backtest_and_persist(
            db,
            strategy_name=request.strategy_name,
            symbol=request.symbol,
            start_ts=request.start_ts,
            end_ts=request.end_ts,
            params=request.params,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e

    return serialize_run(run)