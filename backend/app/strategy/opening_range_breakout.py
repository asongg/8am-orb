from collections import defaultdict
from datetime import time

from app.strategy.base import Strategy
from app.core.types import Signal
from app.core.market_time import market_date, market_time_only


class OpeningRangeBreakoutStrategy(Strategy):
    name = "opening_range_breakout"

    def __init__(self, range_minutes=15, stop_loss_pct=0.005, take_profit_pct=0.01):
        self.range_minutes = range_minutes
        self.stop_loss_pct = stop_loss_pct
        self.take_profit_pct = take_profit_pct
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
        market_close_exit = time(15, 55)

        local_date = market_date(bar.ts)
        local_time = market_time_only(bar.ts)

        if s["session_date"] != local_date:
            s.update({
                "range_high": None,
                "range_low": None,
                "bars_seen": 0,
                "range_complete": False,
                "entered_today": False,
                "session_date": local_date,
            })

        if local_time < market_open or local_time >= time(16, 0):
            return signals

        if not s["range_complete"]:
            s["bars_seen"] += 1
            s["range_high"] = max(s["range_high"] or bar.high, bar.high)
            s["range_low"] = min(s["range_low"] or bar.low, bar.low)

            if s["bars_seen"] >= self.range_minutes:
                s["range_complete"] = True
            return signals

        current_qty = portfolio.position_qty(bar.symbol)
        avg_cost = portfolio.position_avg_cost(bar.symbol)

        if current_qty > 0:
            stop_price = avg_cost * (1 - self.stop_loss_pct)
            take_profit_price = avg_cost * (1 + self.take_profit_pct)

            if bar.close <= stop_price:
                signals.append(
                    Signal(
                        strategy_name=self.name,
                        symbol=bar.symbol,
                        ts=bar.ts,
                        side="SELL",
                        strength=1.0,
                        metadata={"reason": "stop_loss"},
                    )
                )
                return signals

            if bar.close >= take_profit_price:
                signals.append(
                    Signal(
                        strategy_name=self.name,
                        symbol=bar.symbol,
                        ts=bar.ts,
                        side="SELL",
                        strength=1.0,
                        metadata={"reason": "take_profit"},
                    )
                )
                return signals

        if not s["entered_today"] and current_qty == 0 and bar.close > s["range_high"]:
            signals.append(
                Signal(
                    strategy_name=self.name,
                    symbol=bar.symbol,
                    ts=bar.ts,
                    side="BUY",
                    strength=1.0,
                    metadata={"reason": "breakout"},
                )
            )
            s["entered_today"] = True
            return signals

        if current_qty > 0 and local_time >= market_close_exit:
            signals.append(
                Signal(
                    strategy_name=self.name,
                    symbol=bar.symbol,
                    ts=bar.ts,
                    side="SELL",
                    strength=1.0,
                    metadata={"reason": "end_of_day"},
                )
            )

        return signals