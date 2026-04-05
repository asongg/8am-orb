from dataclasses import dataclass


@dataclass
class RiskDecision:
    approved: bool
    reason: str | None = None


class RiskEngine:
    def __init__(self, rules):
        self.rules = rules

    def evaluate(self, signal, portfolio, market_state, context) -> RiskDecision:
        for rule in self.rules:
            result = rule.check(signal, portfolio, market_state, context)
            if not result.ok:
                return RiskDecision(approved=False, reason=result.reason)

        return RiskDecision(approved=True, reason=None)