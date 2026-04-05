from collections import defaultdict


class Portfolio:
    def __init__(self, starting_cash: float = 100_000):
        self.cash = starting_cash
        self.positions = defaultdict(float)
        self.avg_cost = defaultdict(float)
        self.realized_pnl = 0.0
        self.total_equity = starting_cash
        self.last_prices = {}

    def position_qty(self, symbol: str) -> float:
        return self.positions[symbol]

    def position_avg_cost(self, symbol: str) -> float:
        return self.avg_cost[symbol]

    def apply_fill(self, fill):
        symbol = fill["symbol"]
        qty = fill["qty"]
        price = fill["fill_price"]
        commission = fill.get("commission", 0.0)

        if fill["side"] == "BUY":
            current_qty = self.positions[symbol]
            total_cost = self.avg_cost[symbol] * current_qty
            total_cost += qty * price + commission

            new_qty = current_qty + qty
            self.positions[symbol] = new_qty
            self.avg_cost[symbol] = total_cost / new_qty if new_qty != 0 else 0.0
            self.cash -= qty * price + commission

        elif fill["side"] == "SELL":
            current_qty = self.positions[symbol]
            pnl = (price - self.avg_cost[symbol]) * qty - commission
            self.realized_pnl += pnl
            self.positions[symbol] = current_qty - qty
            self.cash += qty * price - commission

            if self.positions[symbol] == 0:
                self.avg_cost[symbol] = 0.0

        self.last_prices[symbol] = price

    def mark_to_market(self, bar):
        self.last_prices[bar.symbol] = bar.close

        market_value = 0.0
        for symbol, qty in self.positions.items():
            last_price = self.last_prices.get(symbol)
            if last_price is not None:
                market_value += qty * last_price

        self.total_equity = self.cash + market_value

    def unrealized_pnl(self) -> float:
        total = 0.0
        for symbol, qty in self.positions.items():
            last_price = self.last_prices.get(symbol)
            if last_price is not None and qty != 0:
                total += qty * (last_price - self.avg_cost[symbol])
        return total