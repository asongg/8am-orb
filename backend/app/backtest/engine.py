class BacktestEngine:
    def __init__(self, strategy, fill_model):
        self.strategy = strategy
        self.fill_model = fill_model

    def run(self, bars, portfolio):
        trades = []
        equity_curve = []

        for bar in bars:
            portfolio.mark_to_market(bar)

            signals = self.strategy.on_bar(bar, portfolio, state={})

            for signal in signals:
                if signal.side == "BUY":
                    qty = 10
                else:
                    qty = portfolio.position_qty(signal.symbol)

                if qty <= 0:
                    continue

                order = {
                    "symbol": signal.symbol,
                    "side": signal.side,
                    "qty": qty,
                }

                fill = self.fill_model.simulate(order, bar)
                portfolio.apply_fill(fill)
                trades.append(fill)

            equity_curve.append({
                "ts": bar.ts,
                "equity": portfolio.total_equity,
            })

        return trades, equity_curve