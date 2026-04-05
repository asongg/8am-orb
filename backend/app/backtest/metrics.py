import numpy as np


def compute_metrics(equity_curve):
    equity = np.array([x["equity"] for x in equity_curve])

    returns = np.diff(equity) / equity[:-1]

    sharpe = 0.0
    if returns.std() > 0:
        sharpe = (returns.mean() / returns.std()) * np.sqrt(252 * 390)

    drawdown = (equity - np.maximum.accumulate(equity)) / np.maximum.accumulate(equity)
    max_drawdown = drawdown.min()

    return {
        "final_equity": float(equity[-1]),
        "sharpe": float(sharpe),
        "max_drawdown": float(max_drawdown),
    }