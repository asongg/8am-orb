from collections import defaultdict
from datetime import time

from app.strategy.base import Strategy
from app.core.types import Signal


class OpeningRangeBreakoutStrategy(Strategy):
    name = "opening_range_breakout"

    def __init__(self, range_minutes=15):
        self.range_minutes = range_minutes
        self.state = defaultdict(lambda: {
            "range_high": None,
            "range_low": None,
            "bars_seen": 0,
            "range_complete": False,
            "entered_today": False,
            "session_date": None,
        })

    def on_bar(self, bar, portfolio, state):
        s = self.state[bar.symbol]
        signals = []

        market_open = time(9, 30)
        session_date = bar.ts.date()

        # Reset daily state
        if s["session_date"] != session_date:
            s.update({
                "range_high": None,
                "range_low": None,
                "bars_seen": 0,
                "range_complete": False,
                "entered_today": False,
                "session_date": session_date,
            })

        # Only trade regular hours
        if bar.ts.time() < market_open or bar.ts.hour >= 16:
            return signals

        # Build opening range
        if not s["range_complete"]:
            s["bars_seen"] += 1
            s["range_high"] = max(s["range_high"] or bar.high, bar.high)
            s["range_low"] = min(s["range_low"] or bar.low, bar.low)

            if s["bars_seen"] >= self.range_minutes:
                s["range_complete"] = True
            return signals

        # Breakout
        if not s["entered_today"] and bar.close > s["range_high"]:
            signals.append(
                Signal(
                    strategy_name=self.name,
                    symbol=bar.symbol,
                    ts=bar.ts,
                    side="BUY",
                    strength=1.0,
                )
            )
            s["entered_today"] = True

        return signals