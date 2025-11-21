import pickle
import matplotlib.pyplot as plt
from matplotlib.colors import LogNorm
import seaborn as sns
import numpy as np
import os
from mpl_toolkits.mplot3d import Axes3D

script_dir = os.path.dirname(os.path.abspath(__file__))
pickle_path = os.path.join(script_dir, "optimal_sc_grids.pkl")
fig_path = os.path.join(script_dir, "figures")

with open(pickle_path, "rb") as f:
    data = pickle.load(f)

# Optimal Return Heatmaps
fig, ax = plt.subplots(ncols=2, figsize=(15, 5))

sns.heatmap(
    np.flipud(data["grids"]["optimal sc-returns"]),
    xticklabels=[f"{x*100:.1f}" for x in data["price volatility space"]],
    yticklabels=[f"{y:.2f}" for y in reversed(data["informed fraction space"])],
    cmap="mako",
    norm=LogNorm(),
    cbar_kws={"label": "Optimal Skew Coefficient"},
    ax=ax[0],
)

sns.heatmap(
    np.flipud(data["grids"]["optimal returns"]),
    xticklabels=[f"{x*100:.1f}" for x in data["price volatility space"]],
    yticklabels=[f"{y:.2f}" for y in reversed(data["informed fraction space"])],
    cmap="mako",
    cbar_kws={"label": "average returns"},
    ax=ax[1],
)

for i in range(len(ax)):
    ax[i].set_xticklabels(ax[i].get_xticklabels(), rotation=45, ha="right")
    ax[i].set_xlabel("Price Volatility (x$10^{-2}$)")
    ax[i].set_ylabel("Informed Trader Fraction")

ax[0].set_title("Optimal Skew Coefficient")
ax[1].set_title("Average Returns At Optimal Skew")

# Optimal msd Heatmaps
fig2, ax2 = plt.subplots(ncols=2, figsize=(15, 5))

sns.heatmap(
    np.flipud(data["grids"]["optimal sc-msd"]),
    xticklabels=[f"{x*100:.1f}" for x in data["price volatility space"]],
    yticklabels=[f"{y:.2f}" for y in reversed(data["informed fraction space"])],
    cmap="mako",
    norm=LogNorm(),
    cbar_kws={"label": "Optimal Skew Coefficient"},
    ax=ax2[0],
)

sns.heatmap(
    np.flipud(data["grids"]["optimal sc-returns"]),
    xticklabels=[f"{x*100:.1f}" for x in data["price volatility space"]],
    yticklabels=[f"{y:.2f}" for y in reversed(data["informed fraction space"])],
    cmap="mako",
    cbar_kws={"label": "optimal Skew Coefficient"},
    norm=LogNorm(),
    ax=ax2[1],
)

for i in range(len(ax)):
    ax2[i].set_xticklabels(ax[i].get_xticklabels(), rotation=45, ha="right")
    ax2[i].set_xlabel("Price Volatility (x$10^{-2}$)")
    ax2[i].set_ylabel("Informed Trader Fraction")

ax2[0].set_title("Optimal MSD Skew Coefficient")
ax2[1].set_title("Optimal Returns Skew Coefficient")

fig.savefig(os.path.join(fig_path, "optimal_skew.png"), dpi=500, bbox_inches="tight")
fig2.savefig(os.path.join(fig_path, "msd_return.png"), dpi=500, bbox_inches="tight")

fig3, ax3 = plt.subplots(ncols=2, subplot_kw={"projection": "3d"})
X, Y = np.meshgrid(data["price volatility space"], data["informed fraction space"])
Z_data = data["grids"]["optimal sc-returns"]
Z_model = np.exp(-9.2612 - 0.5837 * np.log(Y) + 1.0278 * np.log(X))
Z_residuals = Z_data - Z_model
surf = ax3[0].plot_surface(X, Y, Z_data, cmap="mako", alpha=1)
surf2 = ax3[1].plot_surface(X, Y, Z_model, cmap="mako", alpha=1)
ax3[0].view_init(elev=35, azim=130)
ax3[1].view_init(elev=35, azim=130)
fig3.colorbar(surf, ax=ax3, label="Skew Coefficient")

fig4, ax4 = plt.subplots(subplot_kw={"projection": "3d"})
surf3 = ax4.plot_surface(X, Y, Z_residuals, cmap="coolwarm", alpha=1)
ax4.view_init(elev=35, azim=130)
fig3.savefig(os.path.join(fig_path, "surface.png"), dpi=500, bbox_inches="tight")
plt.show()
