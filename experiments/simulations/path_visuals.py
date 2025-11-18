import pickle
import matplotlib.pyplot as plt
from matplotlib.colors import LogNorm
import seaborn as sns
import numpy as np
import os
import pandas as pd


script_dir = os.path.dirname(os.path.abspath(__file__))
file_path = os.path.join(script_dir, "path_visuals.pkl")

with open(file_path, "rb") as f:
    paths = pickle.load(f)

sns.set_theme()

# Determine y axis extent for plots
max_y1 = -float("inf")
min_y1 = float("inf")

max_y2 = -float("inf")
min_y2 = float("inf")

for data in paths.values():
    max_y1 = max(
        data["path data"]["bids"]
        .apply(lambda d: max(d.keys()) if (len(d) > 0) else -float("inf"))
        .max(),
        np.max(data["path data"]["asset value"]),
        max_y1,
    )
    min_y1 = min(
        data["path data"]["asks"]
        .apply(lambda d: min(d.keys()) if (len(d) > 0) else float("inf"))
        .min(),
        np.min(data["path data"]["asset value"]),
        min_y1,
    )
    max_y2 = max(np.max(data["path data"]["mark-to-market"]), max_y2)
    min_y2 = min(np.min(data["path data"]["mark-to-market"]), min_y2)


fig, ax = plt.subplots(
    ncols=3, nrows=2, gridspec_kw={"height_ratios": [2, 1]}, sharey="row"
)

ax[0, 0].set_ylim(min_y1 - 0.5, max_y1 + 0.5)
ax[1, 0].set_ylim(min_y2 - 100, max_y2 + 100)
for j, sc in enumerate(paths):
    path_data = paths[sc]["path data"]
    scatter_data = []
    for i, r in path_data.iterrows():
        for price, volume in r["bids"].items():
            scatter_data.append(
                {"tick": i, "price": price, "volume": volume, "series": "buys"}
            )

        for price, volume in r["asks"].items():
            scatter_data.append(
                {"tick": i, "price": price, "volume": volume, "series": "sells"}
            )

    scatter_df = pd.DataFrame(scatter_data)
    asset_value = path_data["asset value"]
    mid_price = path_data["mid price"]
    mid_df = mid_price.explode().reset_index()
    asset_df = asset_value.explode().reset_index()
    asset_df.columns = ["tick", "price"]
    mid_df.columns = ["tick", "price"]

    sns.scatterplot(
        data=scatter_df,
        x="tick",
        y="price",
        hue="series",
        size="volume",
        sizes=(1, 50),
        edgecolor=None,
        alpha=0.7,
        ax=ax[0, j],
    )
    sns.lineplot(
        data=asset_df,
        x="tick",
        y="price",
        color="black",
        linewidth=0.5,
        label="asset value",
        ax=ax[0, j],
    )
    sns.lineplot(
        data=mid_df,
        x="tick",
        y="price",
        color="blue",
        linewidth=1,
        label="mid price",
        ax=ax[0, j],
    )

    handles, labels = ax[0, j].get_legend_handles_labels()

    filtered = [
        (h, l)
        for h, l in zip(handles, labels)
        if ("volume" not in l.lower())
        and (not l.isnumeric() and "series" not in l.lower())
    ]
    new_handles, new_labels = zip(*filtered)

    ax[0, j].legend(new_handles, new_labels, loc="lower right")

    # Display PnL
    pnl = path_data["mark-to-market"]
    pnl_df = pnl.explode().reset_index()
    pnl_df.columns = ["tick", "mark to market"]
    sns.lineplot(
        pnl_df,
        x="tick",
        y="mark to market",
        color="blue",
        ax=ax[1, j],
    )

plt.show()
