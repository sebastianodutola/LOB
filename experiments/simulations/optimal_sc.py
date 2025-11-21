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


def grid_optimiser(
    metric,
    is_max,
    informed_frac,
    price_vol,
    sc_min,
    sc_max,
    n_sim,
    n_coarse,
    n_fine,
    timesteps,
    seed=1,
):
    rng = np.random.default_rng(seed=seed)

    if is_max:
        optimal = [0, -float("inf")]
    else:
        optimal = [0, float("inf")]

    coarse_sc = np.geomspace(sc_min, sc_max, n_coarse)

    for sc in coarse_sc:
        avg_metrics = simulate(
            informed_frac=informed_frac,
            price_vol=price_vol,
            skew_coefficient=sc,
            n=n_sim,
            rng=rng,
            timesteps=timesteps,
        )
        if is_max:
            if avg_metrics[metric] > optimal[1]:
                optimal = [sc, avg_metrics[metric]]
        else:
            if avg_metrics[metric] < optimal[1]:
                optimal = [sc, avg_metrics[metric]]

    r = coarse_sc[1] / coarse_sc[0]
    k = 1
    hi = optimal[0] * r ** (k)
    lo = optimal[0] * r ** (-k)
    fine_sc = np.geomspace(lo, hi, n_fine)
    for sc in fine_sc:
        avg_metrics = simulate(
            informed_frac=informed_frac,
            price_vol=price_vol,
            skew_coefficient=sc,
            n=n_sim,
            rng=rng,
            timesteps=timesteps,
        )

        if avg_metrics[metric] > optimal[1]:
            optimal = [sc, avg_metrics[metric]]

    return informed_frac, price_vol, optimal


def process_task(args):
    return grid_optimiser(*args)


def optimal_regime(
    informed_frac_space,
    price_vol_space,
    metric,
    is_max,
    sc_min,
    sc_max,
    n_sim,
    n_coarse,
    n_fine,
    timesteps,
    seed,
):
    tasks = [
        (
            metric,
            is_max,
            frac,
            vol,
            sc_min,
            sc_max,
            n_sim,
            n_coarse,
            n_fine,
            timesteps,
            seed,
        )
        for i, frac in enumerate(informed_frac_space)
        for j, vol in enumerate(price_vol_space)
    ]

    with Pool() as pool:
        results = list(tqdm(pool.imap(process_task, tasks), total=len(tasks)))

    m, n = len(informed_frac_space), len(price_vol_space)
    optimal_sc = np.zeros([m, n])
    optimal_values = np.zeros([m, n])

    for frac, vol, optimal in results:
        i = list(informed_frac_space).index(frac)
        j = list(price_vol_space).index(vol)
        optimal_sc[i, j] = optimal[0]
        optimal_values[i, j] = optimal[1]

    return {
        "optimal sc": optimal_sc,
        "optimal": optimal_values,
    }


if __name__ == "__main__":
    sc_min, sc_max = 1e-6, 1e-4
    n_sim = 5
    n_coarse = 20
    n_fine = 10
    informed_frac_space = np.arange(0.1, 1, 0.05)
    price_vol_space = np.arange(0.01, 0.1, 0.005)
    timesteps = 1000
    seed = 1
    res_returns = optimal_regime(
        informed_frac_space,
        price_vol_space,
        "avg returns",
        True,
        sc_min,
        sc_max,
        n_sim,
        n_coarse,
        n_fine,
        timesteps,
        seed,
    )
    res_msd = optimal_regime(
        informed_frac_space,
        price_vol_space,
        metric="value msd",
        is_max=False,
        sc_min=sc_min,
        sc_max=sc_max,
        n_sim=n_sim,
        n_coarse=n_coarse,
        n_fine=n_fine,
        timesteps=timesteps,
        seed=seed,
    )
    res_pnl = optimal_regime(
        informed_frac_space,
        price_vol_space,
        metric="final pnl",
        is_max=True,
        sc_min=sc_min,
        sc_max=sc_max,
        n_sim=n_sim,
        n_coarse=n_coarse,
        n_fine=n_fine,
        timesteps=timesteps,
        seed=seed,
    )
    data = {
        "grids": {
            "optimal sc-returns": res_returns["optimal sc"],
            "optimal returns": res_returns["optimal"],
            "optimal sc-msd": res_msd["optimal sc"],
            "optimal msd": res_msd["optimal"],
            "optimal sc-pnl": res_pnl["optimal sc"],
            "optimal pnl": res_pnl["optimal"],
        },
        "informed fraction space": informed_frac_space,
        "price volatility space": price_vol_space,
    }

    with open(pickle_path, "wb") as f:
        pickle.dump(data, f)
