class SimpleFillModel:
    def __init__(self, slippage_bps=5, commission_per_share=0.0):
        self.slippage_bps = slippage_bps
        self.commission_per_share = commission_per_share

    def simulate(self, order, bar):
        px = bar.close
        slip = self.slippage_bps / 10000.0

        if order["side"] == "BUY":
            fill_price = px * (1 + slip)
        else:
            fill_price = px * (1 - slip)

        qty = order["qty"]
        commission = qty * self.commission_per_share

        return {
            "symbol": order["symbol"],
            "side": order["side"],
            "qty": qty,
            "fill_price": fill_price,
            "fill_ts": bar.ts,
            "commission": commission,
        }