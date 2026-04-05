from collections import defaultdict


class BacktestEngine:
    def __init__(self, strategy, fill_model, fixed_qty=10, risk_engine=None):
        self.strategy = strategy
        self.fill_model = fill_model
        self.fixed_qty = fixed_qty
        self.risk_engine = risk_engine

    def run(self, bars, portfolio):
        trades = []
        equity_curve = []
        risk_events = []

        day_start_equity_by_date = {}

        for bar in bars:
            portfolio.mark_to_market(bar)

            session_date = bar.ts.date()
            if session_date not in day_start_equity_by_date:
                day_start_equity_by_date[session_date] = portfolio.total_equity

            signals = self.strategy.on_bar(bar, portfolio, state={})

            for signal in signals:
                if signal.side == "BUY":
                    qty = self.fixed_qty
                else:
                    qty = portfolio.position_qty(signal.symbol)

                if qty <= 0:
                    continue

                context = {
                    "fixed_qty": self.fixed_qty,
                    "day_start_equity": day_start_equity_by_date[session_date],
                }

                if self.risk_engine is not None:
                    decision = self.risk_engine.evaluate(
                        signal=signal,
                        portfolio=portfolio,
                        market_state={"bar": bar},
                        context=context,
                    )
                    if not decision.approved:
                        risk_events.append({
                            "ts": bar.ts,
                            "strategy_name": signal.strategy_name,
                            "severity": "WARN",
                            "message": f"Signal rejected by risk rule: {decision.reason}",
                            "metadata_json": {
                                "symbol": signal.symbol,
                                "side": signal.side,
                                "reason": decision.reason,
                            },
                        })
                        continue

                order = {
                    "symbol": signal.symbol,
                    "side": signal.side,
                    "qty": qty,
                }

                fill = self.fill_model.simulate(order, bar)
                portfolio.apply_fill(fill)
                trades.append(fill)

            portfolio.mark_to_market(bar)

            equity_curve.append({
                "ts": bar.ts,
                "equity": portfolio.total_equity,
            })

        return trades, equity_curve, risk_events