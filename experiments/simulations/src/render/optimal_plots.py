"""
Visualization tools for market maker skew coefficient optimization results.
Generates heatmaps, 3D surfaces, and comparative analysis plots.
"""

import pickle
import os
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import LogNorm
import seaborn as sns
from mpl_toolkits.mplot3d import Axes3D


def load_data(pickle_path):
    """Load pickled optimization results."""
    with open(pickle_path, "rb") as f:
        return pickle.load(f)


def format_heatmap_axes(ax):
    """Apply consistent axis formatting to heatmaps."""
    ax.set_xticklabels(ax.get_xticklabels(), rotation=45, ha="right")
    ax.set_yticklabels(ax.get_yticklabels(), rotation=0, ha="right")
    ax.set_xlabel("Price Volatility (×$10^{-2}$)")
    ax.set_ylabel("Informed Trader Fraction")


def format_3d_axes(ax):
    """Apply consistent axis formatting to 3d plots."""
    ax.set_xlabel("Price Volatility")
    ax.set_ylabel("Informed Trader Fraction")


def create_dual_heatmap(
    data_left,
    data_right,
    price_vol_space,
    informed_frac_space,
    title_left,
    title_right,
    cbar_label_left,
    cbar_label_right,
    cmap="mako",
    norm_left=None,
    norm_right=None,
    figsize=(15, 5),
):
    """Create side-by-side heatmaps with consistent formatting."""
    fig, axes = plt.subplots(ncols=2, figsize=figsize)

    # Left heatmap
    sns.heatmap(
        np.flipud(data_left),
        xticklabels=[f"{x*100:.1f}" for x in price_vol_space],
        yticklabels=[f"{y:.2f}" for y in reversed(informed_frac_space)],
        cmap=cmap,
        norm=norm_left,
        cbar_kws={"label": cbar_label_left},
        ax=axes[0],
    )
    axes[0].set_title(title_left)

    # Right heatmap
    sns.heatmap(
        np.flipud(data_right),
        xticklabels=[f"{x*100:.1f}" for x in price_vol_space],
        yticklabels=[f"{y:.2f}" for y in reversed(informed_frac_space)],
        cmap=cmap,
        norm=norm_right,
        cbar_kws={"label": cbar_label_right},
        ax=axes[1],
    )
    axes[1].set_title(title_right)

    # Format both axes
    for ax in axes:
        format_heatmap_axes(ax)

    return fig, axes


def create_optimal_return_plots(data, output_dir, dpi=500):
    """Generate heatmaps for optimal skew coefficients and returns."""
    fig, _ = create_dual_heatmap(
        data_left=data["grids"]["optimal sc-returns"],
        data_right=data["grids"]["optimal returns"],
        price_vol_space=data["price volatility space"],
        informed_frac_space=data["informed fraction space"],
        title_left="Optimal Skew Coefficient",
        title_right="Average Returns At Optimal Skew",
        cbar_label_left="Optimal Skew Coefficient",
        cbar_label_right="Average Returns",
        norm_left=LogNorm(),
        norm_right=None,
    )

    fig.savefig(
        os.path.join(output_dir, "optimal_skew.png"), dpi=dpi, bbox_inches="tight"
    )
    return fig


def create_msd_comparison_plots(data, output_dir, dpi=500):
    """Compare MSD-optimized vs return-optimized skew coefficients."""
    fig, _ = create_dual_heatmap(
        data_left=data["grids"]["optimal sc-msd"],
        data_right=data["grids"]["optimal sc-returns"],
        price_vol_space=data["price volatility space"],
        informed_frac_space=data["informed fraction space"],
        title_left="Optimal MSD Skew Coefficient",
        title_right="Optimal Returns Skew Coefficient",
        cbar_label_left="Optimal Skew Coefficient",
        cbar_label_right="Optimal Skew Coefficient",
        norm_left=LogNorm(),
        norm_right=LogNorm(),
    )

    fig.savefig(
        os.path.join(output_dir, "msd_return.png"), dpi=dpi, bbox_inches="tight"
    )
    return fig


def create_surface_plots(data, output_dir, dpi=500):
    """Generate 3D surface plots comparing data to power law model fit."""
    X, Y = np.meshgrid(data["price volatility space"], data["informed fraction space"])

    Z_data = data["grids"]["optimal sc-returns"]
    Z_model = np.exp(-9.2612 - 0.5837 * np.log(Y) + 1.0278 * np.log(X))
    Z_residuals = Z_data - Z_model

    # Data vs model
    fig_surfaces, axes = plt.subplots(
        ncols=2, subplot_kw={"projection": "3d"}, figsize=(15, 6)
    )

    surf1 = axes[0].plot_surface(X, Y, Z_data, cmap="mako", alpha=1)
    axes[0].set_title("Optimal Skew Coefficient (Data)")
    axes[0].view_init(elev=35, azim=130)
    format_3d_axes(axes[0])

    surf2 = axes[1].plot_surface(X, Y, Z_model, cmap="mako", alpha=1)
    axes[1].set_title("Power Law Model Fit")
    axes[1].view_init(elev=35, azim=130)
    format_3d_axes(axes[1])

    fig_surfaces.colorbar(surf1, ax=axes, label="Skew Coefficient", shrink=0.5)

    # Residuals
    fig_residuals, ax_resid = plt.subplots(
        subplot_kw={"projection": "3d"}, figsize=(10, 8)
    )

    surf_resid = ax_resid.plot_surface(X, Y, Z_residuals, cmap="coolwarm", alpha=1)
    ax_resid.set_title("Model Residuals")
    ax_resid.view_init(elev=35, azim=130)
    fig_residuals.colorbar(surf_resid, ax=ax_resid, label="Residuals", shrink=0.5)
    format_3d_axes(ax_resid)

    fig_surfaces.savefig(
        os.path.join(output_dir, "data_model_surface.png"), dpi=dpi, bbox_inches="tight"
    )
    fig_residuals.savefig(
        os.path.join(output_dir, "data_model_residuals_surface.png"),
        dpi=dpi,
        bbox_inches="tight",
    )

    return fig_surfaces, fig_residuals


def create_difference_heatmap(data, output_dir, dpi=500):
    """Show relative difference between return-optimized and MSD-optimized strategies."""
    sc_returns = data["grids"]["optimal sc-returns"]
    sc_msd = data["grids"]["optimal sc-msd"]
    relative_diff = (sc_returns - sc_msd) / np.abs(sc_returns)

    fig, ax = plt.subplots(figsize=(10, 8))

    sns.heatmap(
        np.flipud(relative_diff),
        xticklabels=[f"{x*100:.1f}" for x in data["price volatility space"]],
        yticklabels=[f"{y:.2f}" for y in reversed(data["informed fraction space"])],
        cmap="seismic",
        cbar_kws={"label": "Relative Error in Optimal Skew Coefficient"},
        center=0,
        ax=ax,
    )

    ax.set_title("Return-Optimized vs MSD-Optimized Skew Coefficients")
    format_heatmap_axes(ax)

    fig.savefig(
        os.path.join(output_dir, "msd_returns_difference.png"),
        dpi=dpi,
        bbox_inches="tight",
    )

    return fig


def render_optimisation_figures(data_path, output_dir=None, dpi=500):
    """
    Generate all analysis figures from optimization results.

    Usage:
        render_all_figures('results/optimal_sc_grids.pkl')
        render_all_figures('data.pkl', 'custom_output/', dpi=300)
    """
    # Set up paths
    if output_dir is None:
        script_dir = os.path.dirname(os.path.abspath(data_path))
        output_dir = os.path.join(script_dir, "figures")

    os.makedirs(output_dir, exist_ok=True)

    # Load and generate
    print(f"Loading data from {data_path}...")
    data = load_data(data_path)

    print("Generating optimal return plots...")
    fig_optimal = create_optimal_return_plots(data, output_dir, dpi)

    print("Generating MSD comparison plots...")
    fig_msd = create_msd_comparison_plots(data, output_dir, dpi)

    print("Generating 3D surface plots...")
    fig_surfaces, fig_residuals = create_surface_plots(data, output_dir, dpi)

    print("Generating difference heatmap...")
    fig_difference = create_difference_heatmap(data, output_dir, dpi)

    print(f"All figures saved to {output_dir}")

    return {
        "optimal_return": fig_optimal,
        "msd_comparison": fig_msd,
        "surfaces": fig_surfaces,
        "residuals": fig_residuals,
        "difference": fig_difference,
    }


def main():
    top_dir = os.path.dirname(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    )
    data_path = os.path.join(top_dir, "data/optimal_sc_grids.pkl")

    if not os.path.exists(data_path):
        raise FileNotFoundError(
            f"Data file not found at {data_path}. "
            "Please ensure 'optimal_sc_grids.pkl' exists in the script directory."
        )

    render_optimisation_figures(data_path)


if __name__ == "__main__":
    main()
