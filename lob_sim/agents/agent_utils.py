import numpy as np


def process_market_maker_data(market_maker):
    history = market_maker.history

    # CALCULATE RETURNS

    mtm = np.array(market_maker.history["mark-to-market"])
    returns = np.diff(mtm) / mtm[:-1]
    avg_returns = np.mean(returns)
    final_pnl = mtm[-1]

    # CALCULATE (LOG) SHARPE
    # Sample mean of log returns / sample std of log returns

    log_sharpe = avg_returns / np.std(returns, ddof=1)

    # CALCULATE MARKOUT
    tau = 5
    net_volume = np.array(history["buy volume"]) - np.array(history["sell volume"])
    mid_price = np.array(history["mid price"])
    delta_mp = mid_price[tau:] - mid_price[:-tau]
    markout = np.mean(-(net_volume[:-tau] * delta_mp))

    return {
        "final pnl": final_pnl,
        "avg returns": avg_returns,
        "sharpe": log_sharpe,
        "markout": markout,
    }
