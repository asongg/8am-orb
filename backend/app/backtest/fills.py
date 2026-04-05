class SimpleFillModel:
    def __init__(self, slippage_bps=5):
        self.slippage_bps = slippage_bps

    def simulate(self, order, bar):
        px = bar.close
        slip = self.slippage_bps / 10000

        if order["side"] == "BUY":
            fill_price = px * (1 + slip)
        else:
            fill_price = px * (1 - slip)

        return {
            "symbol": order["symbol"],
            "side": order["side"],
            "qty": order["qty"],
            "fill_price": fill_price,
            "fill_ts": bar.ts,
        }