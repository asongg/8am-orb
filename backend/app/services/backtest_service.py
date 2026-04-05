from datetime import datetime, time, timezone

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.backtest.engine import BacktestEngine
from app.backtest.fills import SimpleFillModel
from app.backtest.metrics import compute_metrics
from app.backtest.portfolio import Portfolio
from app.data.queries import get_bars
from app.models.backtest_run import BacktestRunModel
from app.models.backtest_trade import BacktestTradeModel
from app.models.equity_snapshot import EquitySnapshotModel
from app.models.risk_event import RiskEventModel
from app.risk.engine import RiskEngine
from app.risk.rules import (
    MaxDailyLossRule,
    MaxPositionSizeRule,
    NoDuplicateLongEntryRule,
    NoNewEntriesAfterTimeRule,
)
from app.strategy.opening_range_breakout import OpeningRangeBreakoutStrategy


def build_strategy(strategy_name: str, params: dict):
    if strategy_name == "opening_range_breakout":
        return OpeningRangeBreakoutStrategy(
            range_minutes=params.get("range_minutes", 15),
            stop_loss_pct=params.get("stop_loss_pct", 0.005),
            take_profit_pct=params.get("take_profit_pct", 0.01),
        )
    raise ValueError(f"Unsupported strategy: {strategy_name}")


def build_risk_engine(params: dict) -> RiskEngine:
    cutoff_str = params.get("entry_cutoff_time", "15:30")
    cutoff_hour, cutoff_minute = map(int, cutoff_str.split(":"))

    rules = [
        NoDuplicateLongEntryRule(),
        MaxPositionSizeRule(max_position_size=params.get("max_position_size", 100)),
        NoNewEntriesAfterTimeRule(cutoff_time=time(cutoff_hour, cutoff_minute)),
        MaxDailyLossRule(max_daily_loss=params.get("max_daily_loss", 1000.0)),
    ]
    return RiskEngine(rules)


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

    starting_cash = params.get("starting_cash", 100_000)
    fixed_qty = params.get("fixed_qty", 10)
    slippage_bps = params.get("slippage_bps", 5)
    commission_per_share = params.get("commission_per_share", 0.0)

    strategy = build_strategy(strategy_name, params)
    risk_engine = build_risk_engine(params)
    portfolio = Portfolio(starting_cash=starting_cash)
    fill_model = SimpleFillModel(
        slippage_bps=slippage_bps,
        commission_per_share=commission_per_share,
    )
    engine = BacktestEngine(
        strategy,
        fill_model,
        fixed_qty=fixed_qty,
        risk_engine=risk_engine,
    )

    trades, equity_curve, risk_events = engine.run(bars, portfolio)
    metrics = compute_metrics(equity_curve)
    pnl = metrics["final_equity"] - starting_cash

    run = BacktestRunModel(
        strategy_name=strategy_name,
        params_json={
            "symbol": symbol,
            "range_minutes": getattr(strategy, "range_minutes", None),
            "fixed_qty": fixed_qty,
            "slippage_bps": slippage_bps,
            "commission_per_share": commission_per_share,
            "starting_cash": starting_cash,
            "stop_loss_pct": getattr(strategy, "stop_loss_pct", None),
            "take_profit_pct": getattr(strategy, "take_profit_pct", None),
            "max_position_size": params.get("max_position_size", 100),
            "entry_cutoff_time": params.get("entry_cutoff_time", "15:30"),
            "max_daily_loss": params.get("max_daily_loss", 1000.0),
            "trade_count": len(trades),
            "equity_points": len(equity_curve),
            "risk_event_count": len(risk_events),
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
    db.flush()

    trade_rows = [
        BacktestTradeModel(
            backtest_run_id=run.id,
            symbol=t["symbol"],
            side=t["side"],
            qty=t["qty"],
            fill_price=t["fill_price"],
            fill_ts=t["fill_ts"],
            trade_index=i,
        )
        for i, t in enumerate(trades)
    ]

    snapshot_rows = [
        EquitySnapshotModel(
            backtest_run_id=run.id,
            ts=pt["ts"],
            equity=pt["equity"],
            snapshot_index=i,
        )
        for i, pt in enumerate(equity_curve)
    ]

    risk_rows = [
        RiskEventModel(
            ts=e["ts"],
            strategy_name=e["strategy_name"],
            severity=e["severity"],
            message=e["message"],
            metadata_json={
                **e["metadata_json"],
                "backtest_run_id": str(run.id),
            },
        )
        for e in risk_events
    ]

    db.add_all(trade_rows)
    db.add_all(snapshot_rows)
    db.add_all(risk_rows)
    db.commit()
    db.refresh(run)
    return run


def get_backtest_run(db: Session, run_id: str) -> BacktestRunModel | None:
    stmt = select(BacktestRunModel).where(BacktestRunModel.id == run_id)
    return db.execute(stmt).scalar_one_or_none()


def list_backtest_runs(db: Session) -> list[BacktestRunModel]:
    stmt = select(BacktestRunModel).order_by(BacktestRunModel.created_at.desc())
    return list(db.execute(stmt).scalars().all())


def list_backtest_trades(db: Session, run_id: str) -> list[BacktestTradeModel]:
    stmt = (
        select(BacktestTradeModel)
        .where(BacktestTradeModel.backtest_run_id == run_id)
        .order_by(BacktestTradeModel.trade_index.asc())
    )
    return list(db.execute(stmt).scalars().all())


def list_equity_snapshots(db: Session, run_id: str) -> list[EquitySnapshotModel]:
    stmt = (
        select(EquitySnapshotModel)
        .where(EquitySnapshotModel.backtest_run_id == run_id)
        .order_by(EquitySnapshotModel.snapshot_index.asc())
    )
    return list(db.execute(stmt).scalars().all())


def list_backtest_risk_events(db: Session, run_id: str) -> list[RiskEventModel]:
    stmt = (
        select(RiskEventModel)
        .where(RiskEventModel.metadata_json["backtest_run_id"].astext == run_id)
        .order_by(RiskEventModel.ts.asc())
    )
    return list(db.execute(stmt).scalars().all())