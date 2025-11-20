from tqdm import tqdm
import numpy as np
from multiprocessing import Pool
from lob_sim import simulate_path
import pickle
import os

# data file
script_dir = os.path.dirname(os.path.abspath(__file__))
pickle_path = os.path.join(script_dir, "optimal_sc_grids.pkl")


def simulate(
    informed_frac, skew_coefficient, price_vol=0.05, n=10, timesteps=1000, rng=None
):
    if rng == None:
        rng = np.random.default_rng(seed=42)

    avg_metrics = {}
    for i in range(n):
        metrics = simulate_path(
            price_vol, informed_frac, skew_coefficient, timesteps=timesteps, rng=rng
        )
        if i == 0:
            for k in metrics.keys():
                avg_metrics[k] = 0
        for k, v in metrics.items():
            avg_metrics[k] += v

    for k in metrics.keys():
        avg_metrics[k] /= n

    return avg_metrics


def grid_optimiser(informed_frac, price_vol, skew_search_space, n, timesteps, rng=None):
    max_returns = [0, -float("inf")]
    max_pnl = [0, -float("inf")]
    min_msd = [0, float("inf")]
    for sc in skew_search_space:
        avg_metrics = simulate(
            informed_frac=informed_frac,
            price_vol=price_vol,
            skew_coefficient=sc,
            n=n,
            rng=rng,
            timesteps=timesteps,
        )

        if avg_metrics["final pnl"] > max_pnl[1]:
            max_pnl = [sc, avg_metrics["final pnl"]]
        if avg_metrics["value msd"] < min_msd[1]:
            min_msd = [sc, avg_metrics["value msd"]]
        if avg_metrics["avg returns"] > max_returns[1]:
            max_returns = [sc, avg_metrics["avg returns"]]

    return max_returns, max_pnl, min_msd


def process_market_regime(args):
    frac, vol, skew, n, timesteps, seed = args
    rng = np.random.default_rng(seed=seed)
    max_returns, max_pnl, min_msd = grid_optimiser(
        frac, vol, skew, n=n, timesteps=timesteps, rng=rng
    )
    return frac, vol, [max_returns, max_pnl, min_msd]


def optimal_sharpe_regime(
    informed_frac_space,
    price_vol_space,
    skew_search_space,
    n=3,
    timesteps=500,
    seed=42,
):
    tasks = [
        (frac, vol, skew_search_space, n, timesteps, seed)
        for frac in informed_frac_space
        for vol in price_vol_space
    ]

    with Pool() as pool:
        results = list(tqdm(pool.imap(process_market_regime, tasks), total=len(tasks)))

    m, n = len(informed_frac_space), len(price_vol_space)
    optimal_sc = np.zeros([m, n, 3])
    optimal_values = np.zeros([m, n, 3])

    for frac, vol, maximisers in results:
        i = list(informed_frac_space).index(frac)
        j = list(price_vol_space).index(vol)
        for k in range(3):
            optimal_sc[i, j, k] = maximisers[k][0]
            optimal_values[i, j, k] = maximisers[k][1]

    return {
        "optimal sc-returns": optimal_sc[:, :, 0],
        "optimal returns": optimal_values[:, :, 0],
        "optimal sc-pnl": optimal_sc[:, :, 1],
        "optimal pnl": optimal_values[:, :, 1],
        "optimal sc-msd": optimal_sc[:, :, 2],
        "optimal msd": optimal_values[:, :, 2],
    }


if __name__ == "__main__":
    skew_coefficients = np.concat(
        [np.arange(1e-6, 1e-5, 2.5e-7), np.arange(1e-5, 1e-4, 2.5e-6)]
    )
    informed_frac_space = np.arange(0.1, 1, 0.05)
    price_vol_space = np.arange(0.01, 0.1, 0.005)
    n = 5
    timesteps = 1000
    seed = 1
    res = optimal_sharpe_regime(
        informed_frac_space,
        price_vol_space,
        skew_coefficients,
        n=n,
        timesteps=timesteps,
        seed=seed,
    )
    data = {
        "grids": res,
        "informed fraction space": informed_frac_space,
        "price volatility space": price_vol_space,
    }

    with open(pickle_path, "wb") as f:
        pickle.dump(data, f)
