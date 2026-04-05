from dataclasses import dataclass
from datetime import time

from app.core.market_time import market_time_only


@dataclass
class RuleResult:
    ok: bool
    reason: str | None = None


class NoDuplicateLongEntryRule:
    def check(self, signal, portfolio, market_state, context) -> RuleResult:
        if signal.side == "BUY" and portfolio.position_qty(signal.symbol) > 0:
            return RuleResult(ok=False, reason="duplicate_long_entry")
        return RuleResult(ok=True)


class MaxPositionSizeRule:
    def __init__(self, max_position_size: float):
        self.max_position_size = max_position_size

    def check(self, signal, portfolio, market_state, context) -> RuleResult:
        fixed_qty = context["fixed_qty"]
        current_qty = portfolio.position_qty(signal.symbol)

        if signal.side == "BUY":
            projected_qty = current_qty + fixed_qty
        else:
            projected_qty = 0.0

        if abs(projected_qty) > self.max_position_size:
            return RuleResult(ok=False, reason="max_position_size_exceeded")
        return RuleResult(ok=True)


class NoNewEntriesAfterTimeRule:
    def __init__(self, cutoff_time: time):
        self.cutoff_time = cutoff_time

    def check(self, signal, portfolio, market_state, context) -> RuleResult:
        bar = market_state["bar"]
        local_time = market_time_only(bar.ts)

        if signal.side == "BUY" and local_time >= self.cutoff_time:
            return RuleResult(ok=False, reason="entry_after_cutoff")
        return RuleResult(ok=True)


class MaxDailyLossRule:
    def __init__(self, max_daily_loss: float):
        self.max_daily_loss = max_daily_loss

    def check(self, signal, portfolio, market_state, context) -> RuleResult:
        day_start_equity = context["day_start_equity"]
        current_equity = portfolio.total_equity

        if day_start_equity - current_equity >= self.max_daily_loss:
            return RuleResult(ok=False, reason="max_daily_loss_exceeded")
        return RuleResult(ok=True)