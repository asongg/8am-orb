from dataclasses import dataclass

@dataclass
class RiskDecision:
    approved: bool
    order_request: object | None = None
    reason: str | None = None

class RiskEngine:
    def __init__(self, rules, sizing_fn):
        self.rules = rules
        self.sizing_fn = sizing_fn

    def validate(self, signal, portfolio, market_state):
        for rule in self.rules:
            ok, reason = rule.check(signal, portfolio, market_state)
            if not ok:
                return RiskDecision(approved=False, reason=reason)

        qty = self.sizing_fn(signal, portfolio, market_state)
        return RiskDecision(
            approved=True,
            order_request={
                "strategy_name": signal.strategy_name,
                "symbol": signal.symbol,
                "side": signal.side,
                "qty": qty,
                "order_type": "MARKET",
            },
        )s