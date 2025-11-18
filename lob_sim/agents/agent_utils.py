import numpy as np


def process_market_maker_data(market_maker):
    history = market_maker.history

    # CALCULATE LOG RETURNS

    mtm = np.array(market_maker.history["mark-to-market"])
    log_rt = np.diff(np.log(mtm))
    avg_rt = np.mean(log_rt)
    final_pnl = mtm[-1]

    # CALCULATE (LOG) SHARPE
    # Sample mean of log returns / sample std of log returns

    log_sharpe = avg_rt / np.std(log_rt, ddof=1)

    # CALCULATE MARKOUT
    tau = 5
    net_volume = np.array(history["buy volume"]) - np.array(history["sell volume"])
    mid_price = np.array(history["mid price"])
    delta_mp = mid_price[tau:] - mid_price[:-tau]
    markout = np.mean(-(net_volume[:-tau] * delta_mp))

    return {
        "final pnl": final_pnl,
        "avg log returns": avg_rt,
        "sharpe": log_sharpe,
        "markout": markout,
    }
