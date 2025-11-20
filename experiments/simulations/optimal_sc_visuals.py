import pickle
import matplotlib.pyplot as plt
from matplotlib.colors import LogNorm
import seaborn as sns
import numpy as np
import os

script_dir = os.path.dirname(os.path.abspath(__file__))
pickle_path = os.path.join(script_dir, "optimal_sc_grids.pkl")

with open(pickle_path, "rb") as f:
    data = pickle.load(f)

fig, ax = plt.subplots(ncols=2, figsize=(15, 5))


sns.heatmap(
    data["grids"]["optimal sc-returns"],
    xticklabels=[f"{x*100:.1f}" for x in data["price volatility space"]],
    yticklabels=[f"{y:.2f}" for y in data["informed fraction space"]],
    cmap="mako",
    norm=LogNorm(),
    cbar_kws={"label": "Optimal Skew Coefficient"},
    ax=ax[0],
)

sns.heatmap(
    data["grids"]["optimal returns"],
    xticklabels=[f"{x*100:.1f}" for x in data["price volatility space"]],
    yticklabels=[f"{y:.2f}" for y in data["informed fraction space"]],
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
plt.show()
