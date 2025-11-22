"""
Market maker trajectory data generation.
Simulates and saves market maker paths for visualization and analysis.
"""

import os
import pickle
import numpy as np
import pandas as pd
from lob_sim import simulate_path_with_tracking


def create_path_dataframe(simulation_results):
    """Convert simulation results dict to dataframe."""
    return pd.DataFrame(
        {
            "bids": simulation_results["bids"],
            "asks": simulation_results["asks"],
            "asset value": simulation_results["asset value"],
            "mid price": simulation_results["mid price"],
            "mark-to-market": simulation_results["mark-to-market"],
        }
    )


def generate_trajectories(price_vol, informed_frac, skew_coef, timesteps=1000, seed=40):
    """
    Generate market maker trajectory data.

    Returns single path dict if skew_coef is scalar,
    or dict of paths keyed by coefficient if skew_coef is list.
    """
    # Handle both single coefficient and list
    is_single = not isinstance(skew_coef, (list, tuple, np.ndarray))
    skew_list = [skew_coef] if is_single else skew_coef

    paths = {}
    for sc in skew_list:
        rng = np.random.default_rng(seed=seed)
        results = simulate_path_with_tracking(
            price_vol, informed_frac, sc, rng=rng, timesteps=timesteps
        )

        path_df = create_path_dataframe(results)
        paths[sc] = {"path data": path_df, "summary stats": results["summary stats"]}

    # Return single path dict if only one coefficient, otherwise return full dict
    return paths[skew_coef] if is_single else paths


def save_pickle(data, filepath):
    """Save data to pickle file."""
    with open(filepath, "wb") as f:
        pickle.dump(data, f)


def main():
    top_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    # Generate single long trajectory
    print("Generating single trajectory (skew=5e-6, steps=1000)...")
    single_path = generate_trajectories(
        price_vol=0.05, informed_frac=0.5, skew_coef=5e-6, timesteps=1000, seed=40
    )
    single_path_file = os.path.join(top_dir, "data/single_trajectory.pkl")
    save_pickle(single_path, single_path_file)
    print(f"Saved to {single_path_file}")

    # Generate comparison trajectories
    comparison_skews = [1e-6, 5e-6, 2e-5]
    print(f"Generating comparison trajectories (skews={comparison_skews}, steps=50)...")
    comparison_paths = generate_trajectories(
        price_vol=0.05,
        informed_frac=0.5,
        skew_coef=comparison_skews,
        timesteps=50,
        seed=40,
    )
    comparison_path_file = os.path.join(top_dir, "data/trajectory_comparison.pkl")
    save_pickle(comparison_paths, comparison_path_file)
    print(f"Saved to {comparison_path_file}")

    print("Trajectory generation complete.")


if __name__ == "__main__":
    main()
