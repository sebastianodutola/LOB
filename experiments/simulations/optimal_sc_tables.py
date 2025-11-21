import pandas as pd
import numpy as np
from rich.console import Console
from rich.table import Table
import pickle
import os
import statsmodels.api as sm

script_dir = os.path.dirname(os.path.abspath(__file__))
pickle_path = os.path.join(script_dir, "optimal_sc_grids.pkl")

with open(pickle_path, "rb") as f:
    data = pickle.load(f)

optimal_sc_returns = data["grids"]["optimal sc-returns"]
optimal_returns = data["grids"]["optimal returns"]
optimal_sc_pnl = data["grids"]["optimal sc-pnl"]
optimal_pnl = data["grids"]["optimal pnl"]
optimal_sc_msd = data["grids"]["optimal sc-msd"]

informed_frac_space = data["informed fraction space"]
price_volatility_space = data["price volatility space"]

# Check the difference between optimal skew coefficient based on returns vs pnl
print(np.max(optimal_sc_pnl - optimal_sc_msd))  # = 0

optimal_sc_data = []
for i in range(len(informed_frac_space)):
    for j in range(len(price_volatility_space)):
        optimal_sc_data.append(
            {
                "informed fraction": informed_frac_space[i],
                "price volatility": price_volatility_space[j],
                "optimal coefficient": optimal_sc_returns[i, j],
                "average returns": optimal_returns[i, j],
                "final pnl": optimal_pnl[i, j],
            }
        )

df = pd.DataFrame(optimal_sc_data)

# linear regression
X = np.log(df[["informed fraction", "price volatility"]])
X = sm.add_constant(X)
y = np.log(df["optimal coefficient"])

df["optimal coefficient"] = df["optimal coefficient"].apply(lambda x: f"{x:.6e}")
df["average returns"] = df["average returns"].apply(lambda x: f"{x:.6e}")
fixed_if_df = df[
    ((df["informed fraction"] - 0.5).abs() < 1e-12)
    & ((df["price volatility"] * 1000).round() % 20 == 0)
]

fixed_pv_df = df[
    ((df["price volatility"] - 0.05).abs() < 1e-12)
    & ((df["informed fraction"] * 100).round() % 20 == 0)
]

model = sm.OLS(y, X).fit()
print(model.summary())

console = Console()
console.print(fixed_if_df)
console.print(fixed_pv_df)
