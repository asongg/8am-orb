class MaxPositionSizeRule:
    def __init__(self, max_shares: float):
        self.max_shares = max_shares

    def check(self, signal, portfolio, market_state):
        current = portfolio.position_qty(signal.symbol)
        projected = current + 100 if signal.side == "BUY" else current - 100
        if abs(projected) > self.max_shares:
            return False, "max_position_size_exceeded"
        return True, None