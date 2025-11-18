from lob_sim import simulate_path_with_tracking, process_market_maker_data
import pandas as pd
import numpy as np
import pickle
import os

# Force save relative to your script
script_dir = os.path.dirname(os.path.abspath(__file__))
file_path = os.path.join(script_dir, "path_visuals.pkl")
skew_coefficient = [1e-6, 5e-6, 2e-5]
paths = {}

for sc in skew_coefficient:
    rng = np.random.default_rng(seed=40)
    res = simulate_path_with_tracking(0.05, 0.5, sc, rng=rng, timesteps=50)
    path_df = pd.DataFrame(
        {
            "bids": res["bids"],
            "asks": res["asks"],
            "asset value": res["asset value"],
            "mid price": res["mid price"],
            "mark-to-market": res["mark-to-market"],
        }
    )
    paths[sc] = {"path data": path_df, "summary stats": res["summary stats"]}

with open(file_path, "wb") as f:
    pickle.dump(paths, f)
