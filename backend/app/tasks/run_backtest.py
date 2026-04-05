from datetime import datetime, timezone

from app.db import SessionLocal
from app.services.backtest_service import run_backtest_and_persist


def main():
    with SessionLocal() as db:
        run = run_backtest_and_persist(
            db,
            strategy_name="opening_range_breakout",
            symbol="SPY",
            start_ts=datetime(2026, 3, 30, tzinfo=timezone.utc),
            end_ts=datetime(2026, 4, 4, tzinfo=timezone.utc),
            params={
                "range_minutes": 15,
                "fixed_qty": 10,
                "slippage_bps": 5,
                "starting_cash": 100_000,
            },
        )

        print("Saved backtest run:", run.id)
        print("PnL:", run.pnl)
        print("Sharpe:", run.sharpe)
        print("Max drawdown:", run.max_drawdown)


if __name__ == "__main__":
    main()