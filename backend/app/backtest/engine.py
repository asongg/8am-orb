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
                order = {
                    "symbol": signal.symbol,
                    "side": signal.side,
                    "qty": 10,
                }

                fill = self.fill_model.simulate(order, bar)
                portfolio.apply_fill(fill)
                trades.append(fill)

            equity_curve.append({
                "ts": bar.ts,
                "equity": portfolio.total_equity,
            })

        return trades, equity_curve