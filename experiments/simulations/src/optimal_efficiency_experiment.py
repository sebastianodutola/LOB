import numpy as np
import pickle
import os
from tqdm import tqdm
from lob_sim import simulate_path
from multiprocessing import Pool


def simulate(
    informed_frac, skew_coefficient, price_vol=0.05, n=10, timesteps=1000, rng=None
):
    """Run multiple simulations and return averaged metrics."""
    if rng is None:
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


def regime_optimality_loss(i, j, informed_frac, price_vol, sc_ret, sc_msd, n, seed):
    rng1 = np.random.default_rng(seed=seed)
    rng2 = np.random.default_rng(seed=seed)

    avg_metrics_sc_ret = simulate(informed_frac, sc_ret, price_vol, n, rng=rng1)
    avg_metrics_sc_msd = simulate(informed_frac, sc_msd, price_vol, n, rng=rng2)

    L_ret_sc_ret = avg_metrics_sc_ret["avg returns"]
    L_ret_sc_msd = avg_metrics_sc_msd["avg returns"]

    L_msd_sc_ret = avg_metrics_sc_ret["value msd"]
    L_msd_sc_msd = avg_metrics_sc_msd["value msd"]

    optimal_ret = L_ret_sc_ret
    optimality_loss_ret_abs = L_ret_sc_ret - L_ret_sc_msd
    optimality_loss_ret = (L_ret_sc_ret - L_ret_sc_msd) / L_ret_sc_msd
    optimality_loss_msd = (L_msd_sc_ret - L_msd_sc_msd) / L_msd_sc_msd

    return (
        i,
        j,
        optimal_ret,
        optimality_loss_ret_abs,
        optimality_loss_ret,
        optimality_loss_msd,
    )


def process_task(args):
    return regime_optimality_loss(*args)


def optimality_loss(
    optimal_sc_ret,
    optimal_sc_msd,
    informed_frac_space,
    price_vol_space,
    n_sim=10,
    seed=42,
):
    rng = np.random.default_rng(seed=seed)
    n, m = optimal_sc_ret.shape
    optimality_loss_ret = np.zeros([n, m])
    optimal_ret = np.zeros_like(optimality_loss_ret)
    optimality_loss_ret_abs = np.zeros_like(optimality_loss_ret)
    optimality_loss_msd = np.zeros_like(optimality_loss_ret)

    tasks = []
    for i in range(n):
        for j in range(m):
            seed = rng.integers(1 << 32)
            frac = informed_frac_space[i]
            vol = price_vol_space[j]
            sc_ret = optimal_sc_ret[i, j]
            sc_msd = optimal_sc_msd[i, j]
            tasks.append((i, j, frac, vol, sc_ret, sc_msd, n_sim, seed))

    with Pool() as pool:
        results = list(tqdm(pool.imap(process_task, tasks), total=len(tasks)))

    for res in results:
        i = res[0]
        j = res[1]
        optimal_ret[i, j] = res[2]
        optimality_loss_ret_abs[i, j] = res[3]
        optimality_loss_ret[i, j] = res[4]
        optimality_loss_msd[i, j] = res[5]

    return {
        "optimal returns": optimal_ret,
        "optimality loss absolute returns": optimality_loss_ret_abs,
        "optimality loss returns": optimality_loss_ret,
        "optimality loss msd": optimality_loss_msd,
        "informed fraction space": informed_frac_space,
        "price volatility space": price_vol_space,
    }


def run_optimality_comparison(data_path, output_path):

    with open(data_path, "rb") as f:
        data = pickle.load(f)

    optimal_sc_ret = data["grids"]["optimal sc-returns"]
    optimal_sc_msd = data["grids"]["optimal sc-msd"]
    informed_frac_space = data["informed fraction space"]
    price_vol_space = data["price volatility space"]
    res = optimality_loss(
        optimal_sc_ret,
        optimal_sc_msd,
        informed_frac_space,
        price_vol_space,
        n_sim=10,
    )

    with open(output_path, "wb") as f:
        pickle.dump(res, f)


def main():
    top_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    output_path = os.path.join(top_dir, "data/optimality_loss.pkl")
    data_path = os.path.join(top_dir, "data/optimal_grids.pkl")
    run_optimality_comparison(data_path, output_path)


if __name__ == "__main__":
    main()
