from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.backtest.engine import BacktestEngine
from app.backtest.fills import SimpleFillModel
from app.backtest.metrics import compute_metrics
from app.backtest.portfolio import Portfolio
from app.data.queries import get_bars
from app.models.backtest_run import BacktestRunModel
from app.strategy.opening_range_breakout import OpeningRangeBreakoutStrategy


def build_strategy(strategy_name: str, params: dict):
    if strategy_name == "opening_range_breakout":
        return OpeningRangeBreakoutStrategy(
            range_minutes=params.get("range_minutes", 15)
        )
    raise ValueError(f"Unsupported strategy: {strategy_name}")


def run_backtest_and_persist(
    db: Session,
    *,
    strategy_name: str,
    symbol: str,
    start_ts: datetime,
    end_ts: datetime,
    params: dict,
) -> BacktestRunModel:
    bars = get_bars(db, symbol, start_ts, end_ts)

    if not bars:
        raise ValueError("No bars found for requested symbol/time range")

    strategy = build_strategy(strategy_name, params)
    portfolio = Portfolio(starting_cash=params.get("starting_cash", 100_000))
    fill_model = SimpleFillModel(slippage_bps=params.get("slippage_bps", 5))
    engine = BacktestEngine(strategy, fill_model)

    trades, equity_curve = engine.run(bars, portfolio)
    metrics = compute_metrics(equity_curve)

    starting_cash = params.get("starting_cash", 100_000)
    pnl = metrics["final_equity"] - starting_cash

    run = BacktestRunModel(
        strategy_name=strategy_name,
        params_json={
            "symbol": symbol,
            "range_minutes": getattr(strategy, "range_minutes", None),
            "fixed_qty": params.get("fixed_qty", 10),
            "slippage_bps": fill_model.slippage_bps,
            "starting_cash": starting_cash,
            "trade_count": len(trades),
        },
        start_ts=start_ts,
        end_ts=end_ts,
        pnl=pnl,
        sharpe=metrics["sharpe"],
        max_drawdown=metrics["max_drawdown"],
        win_rate=None,
        created_at=datetime.now(timezone.utc),
    )

    db.add(run)
    db.commit()
    db.refresh(run)
    return run


def get_backtest_run(db: Session, run_id: str) -> BacktestRunModel | None:
    stmt = select(BacktestRunModel).where(BacktestRunModel.id == run_id)
    return db.execute(stmt).scalar_one_or_none()


def list_backtest_runs(db: Session) -> list[BacktestRunModel]:
    stmt = select(BacktestRunModel).order_by(BacktestRunModel.created_at.desc())
    return list(db.execute(stmt).scalars().all())