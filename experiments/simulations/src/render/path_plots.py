"""
Market maker trajectory visualization tools.
Plots price paths, order flow, and PnL for simulated market maker strategies.
"""

import pickle
import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns


def load_data(pickle_path):
    """Load pickled simulation path data."""
    with open(pickle_path, "rb") as f:
        return pickle.load(f)


def extract_scatter_data(path_data):
    """Convert bid/ask dictionaries to plottable scatter dataframe."""
    scatter_data = []
    for i, row in path_data.iterrows():
        for price, volume in row["bids"].items():
            scatter_data.append(
                {"tick": i, "price": price, "volume": volume, "series": "buys"}
            )
        for price, volume in row["asks"].items():
            scatter_data.append(
                {"tick": i, "price": price, "volume": volume, "series": "sells"}
            )
    return pd.DataFrame(scatter_data)


def compute_axis_limits(path_data_list):
    """Calculate shared y-axis limits across multiple paths."""
    max_price = -float("inf")
    min_price = float("inf")
    max_pnl = -float("inf")
    min_pnl = float("inf")

    for path_data in path_data_list:
        max_price = max(
            path_data["bids"]
            .apply(lambda d: max(d.keys()) if len(d) > 0 else -float("inf"))
            .max(),
            np.max(path_data["asset value"]),
            max_price,
        )
        min_price = min(
            path_data["asks"]
            .apply(lambda d: min(d.keys()) if len(d) > 0 else float("inf"))
            .min(),
            np.min(path_data["asset value"]),
            min_price,
        )
        max_pnl = max(np.max(path_data["mark-to-market"]), max_pnl)
        min_pnl = min(np.min(path_data["mark-to-market"]), min_pnl)

    return (min_price - 0.5, max_price + 0.5), (min_pnl - 100, max_pnl + 100)


def plot_trajectory_on_axes(path_data, ax_price, ax_pnl, title=None):
    """Plot price trajectory and PnL on provided axes."""
    # Prepare data
    scatter_df = extract_scatter_data(path_data)

    asset_df = path_data["asset value"].explode().reset_index()
    asset_df.columns = ["tick", "price"]

    mid_df = path_data["mid price"].explode().reset_index()
    mid_df.columns = ["tick", "price"]

    pnl_df = path_data["mark-to-market"].explode().reset_index()
    pnl_df.columns = ["tick", "mark to market"]

    # Plot price trajectory
    sns.scatterplot(
        data=scatter_df,
        x="tick",
        y="price",
        hue="series",
        size="volume",
        sizes=(1, 50),
        edgecolor=None,
        alpha=0.7,
        ax=ax_price,
    )
    sns.lineplot(
        data=asset_df,
        x="tick",
        y="price",
        color="black",
        linewidth=0.8,
        label="asset value",
        ax=ax_price,
    )
    sns.lineplot(
        data=mid_df,
        x="tick",
        y="price",
        color="yellowgreen",
        linewidth=1.5,
        label="mid price",
        ax=ax_price,
    )

    # Clean up legend (remove volume sizes and series)
    handles, labels = ax_price.get_legend_handles_labels()
    filtered = [
        (h, l)
        for h, l in zip(handles, labels)
        if "volume" not in l.lower() and not l.isnumeric() and "series" not in l.lower()
    ]
    if filtered:
        new_handles, new_labels = zip(*filtered)
        ax_price.legend(new_handles, new_labels, loc="lower right")

    if title:
        ax_price.set_title(title)

    # Plot PnL
    sns.lineplot(
        pnl_df,
        x="tick",
        y="mark to market",
        color="blue",
        ax=ax_pnl,
    )


def plot_single_trajectory(path, output_dir, filename="single_trajectory.png", dpi=500):
    """Create figure with single trajectory and PnL plot."""
    sns.set_theme()

    path_data = path["path data"]
    price_lim, pnl_lim = compute_axis_limits([path_data])

    fig, axes = plt.subplots(
        nrows=2,
        gridspec_kw={"height_ratios": [2, 1]},
        figsize=(10, 8),
    )

    axes[0].set_ylim(*price_lim)
    axes[1].set_ylim(*pnl_lim)

    plot_trajectory_on_axes(path_data, axes[0], axes[1], title="Simulated Trajectory")

    plt.tight_layout()
    fig.savefig(os.path.join(output_dir, filename), dpi=dpi, bbox_inches="tight")

    return fig


def plot_trajectory_comparison(
    paths, output_dir, filename="trajectory_comparison.png", dpi=500
):
    """Create figure comparing multiple trajectories side-by-side."""
    sns.set_theme()

    n_paths = len(paths)
    path_data_list = [data["path data"] for data in paths.values()]
    price_lim, pnl_lim = compute_axis_limits(path_data_list)

    fig, axes = plt.subplots(
        ncols=n_paths,
        nrows=2,
        gridspec_kw={"height_ratios": [2, 1]},
        sharey="row",
        figsize=(10, 8),
    )

    axes[0, 0].set_ylim(*price_lim)
    axes[1, 0].set_ylim(*pnl_lim)

    for j, (param, data) in enumerate(paths.items()):
        path_data = data["path data"]
        plot_trajectory_on_axes(
            path_data, axes[0, j], axes[1, j], title=f"Skew coefficient: {param}"
        )

    plt.tight_layout()
    fig.savefig(os.path.join(output_dir, filename), dpi=dpi, bbox_inches="tight")

    return fig


def render_trajectory_figures(
    comparison_data_path=None, single_data_path=None, output_dir=None, dpi=500
):
    """
    Generate trajectory visualization figures.

    Usage:
        render_trajectory_figures('sc_path_visuals.pkl', 'full_path_visuals.pkl')
        render_trajectory_figures(single_data_path='path.pkl', dpi=300)
    """
    if output_dir is None:
        if comparison_data_path:
            script_dir = os.path.dirname(os.path.abspath(comparison_data_path))
        elif single_data_path:
            script_dir = os.path.dirname(os.path.abspath(single_data_path))
        else:
            script_dir = os.path.dirname(os.path.abspath(__file__))
        output_dir = os.path.join(script_dir, "figures")

    os.makedirs(output_dir, exist_ok=True)

    figures = {}

    # Generate comparison plot if data provided
    if comparison_data_path:
        print(f"Loading comparison data from {comparison_data_path}...")
        paths = load_data(comparison_data_path)
        print(f"Generating trajectory comparison ({len(paths)} scenarios)...")
        fig_comparison = plot_trajectory_comparison(
            paths, output_dir, "trajectory_comparison.png", dpi
        )
        figures["comparison"] = fig_comparison

    # Generate single trajectory plot if data provided
    if single_data_path:
        print(f"Loading single trajectory data from {single_data_path}...")
        path = load_data(single_data_path)
        print("Generating single trajectory plot...")
        fig_single = plot_single_trajectory(
            path, output_dir, "single_trajectory.png", dpi
        )
        figures["single"] = fig_single

    print(f"All figures saved to {output_dir}")

    return figures


def main():
    top_dir = os.path.dirname(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    )
    comparison_path = os.path.join(top_dir, "data/trajectory_comparison.pkl")
    single_path = os.path.join(top_dir, "data/single_trajectory.pkl")

    # Check which files exist
    has_comparison = os.path.exists(comparison_path)
    has_single = os.path.exists(single_path)

    if not has_comparison and not has_single:
        raise FileNotFoundError(
            f"No data files found. Expected:\n"
            f"  - {comparison_path}\n"
            f"  - {single_path}"
        )

    render_trajectory_figures(
        comparison_data_path=comparison_path if has_comparison else None,
        single_data_path=single_path if has_single else None,
    )


if __name__ == "__main__":
    main()
