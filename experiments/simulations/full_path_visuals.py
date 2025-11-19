import pickle
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import os
import pandas as pd


script_dir = os.path.dirname(os.path.abspath(__file__))
data_file_path = os.path.join(script_dir, "full_path_visuals.pkl")
figure_dir = os.path.join(script_dir, "figures")

with open(data_file_path, "rb") as f:
    path = pickle.load(f)

sns.set_theme()

# Determine y axis extent for sc plots
max_y1 = -float("inf")
min_y1 = float("inf")

max_y2 = -float("inf")
min_y2 = float("inf")


max_y1 = max(
    path["path data"]["bids"]
    .apply(lambda d: max(d.keys()) if (len(d) > 0) else -float("inf"))
    .max(),
    np.max(path["path data"]["asset value"]),
    max_y1,
)
min_y1 = min(
    path["path data"]["asks"]
    .apply(lambda d: min(d.keys()) if (len(d) > 0) else float("inf"))
    .min(),
    np.min(path["path data"]["asset value"]),
    min_y1,
)
max_y2 = max(np.max(path["path data"]["mark-to-market"]), max_y2)
min_y2 = min(np.min(path["path data"]["mark-to-market"]), min_y2)


fig, ax = plt.subplots(
    nrows=2,
    gridspec_kw={"height_ratios": [2, 1]},
    figsize=(15, 10),
)

ax[0].set_ylim(min_y1 - 0.5, max_y1 + 0.5)
ax[1].set_ylim(min_y2 - 100, max_y2 + 100)

path_data = path["path data"]
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
    ax=ax[0],
)
sns.lineplot(
    data=asset_df,
    x="tick",
    y="price",
    color="black",
    linewidth=0.8,
    label="asset value",
    ax=ax[0],
)
sns.lineplot(
    data=mid_df,
    x="tick",
    y="price",
    color="yellowgreen",
    linewidth=1.5,
    label="mid price",
    ax=ax[0],
)

handles, labels = ax[0].get_legend_handles_labels()

filtered = [
    (h, l)
    for h, l in zip(handles, labels)
    if ("volume" not in l.lower()) and (not l.isnumeric() and "series" not in l.lower())
]
new_handles, new_labels = zip(*filtered)

ax[0].legend(new_handles, new_labels, loc="lower right")

ax[0].set_title(f"Simulated Trajectory")

# Display PnL
pnl = path_data["mark-to-market"]
pnl_df = pnl.explode().reset_index()
pnl_df.columns = ["tick", "mark to market"]
sns.lineplot(
    pnl_df,
    x="tick",
    y="mark to market",
    color="blue",
    ax=ax[1],
)


plt.tight_layout()
fig.savefig(os.path.join(figure_dir, "fig2.png"), dpi=500, bbox_inches="tight")
