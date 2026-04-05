from datetime import datetime, timezone

from app.db import SessionLocal
from app.data.queries import get_bars
from app.strategy.opening_range_breakout import OpeningRangeBreakoutStrategy
from app.backtest.engine import BacktestEngine
from app.backtest.portfolio import Portfolio
from app.backtest.fills import SimpleFillModel
from app.backtest.metrics import compute_metrics


def main():
    symbol = "SPY"

    start = datetime(2026, 3, 30, tzinfo=timezone.utc)
    end = datetime(2026, 4, 4, tzinfo=timezone.utc)

    with SessionLocal() as db:
        bars = get_bars(db, symbol, start, end)

    print(f"Loaded {len(bars)} bars")

    strategy = OpeningRangeBreakoutStrategy()
    portfolio = Portfolio()
    fill_model = SimpleFillModel()

    engine = BacktestEngine(strategy, fill_model)

    trades, equity_curve = engine.run(bars, portfolio)

    metrics = compute_metrics(equity_curve)

    print("Trades:", len(trades))
    print("Metrics:", metrics)


if __name__ == "__main__":
    main()