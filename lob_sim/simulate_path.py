from lob_sim import (
    OrderBook,
    MarketMaker,
    SkewMarketMakingStrategy,
    InformedTraders,
    Asset,
    process_market_maker_data,
)
from itertools import chain
import numpy as np
import matplotlib.pyplot as plt


def simulate_path_with_tracking(
    price_volatility, informed_frac, skew_coefficient, timesteps=1000, rng=None
):

    if rng == None:
        rng = np.random.default_rng(seed=42)

    # Initialise agents and asset
    a = Asset(sigma=price_volatility)
    ob = OrderBook()
    strat = SkewMarketMakingStrategy(0.1, 1000, skew_coefficient)
    mm = MarketMaker(strat, initial_capital=1_000_000)
    it = InformedTraders(informed_frac, 25, 10)

    # Track trades
    asset_value = []
    mid_price = []
    bids = []
    asks = []

    # Simulation Loop
    mm_notifications = []
    for _ in range(timesteps):
        bids_tick = {}
        asks_tick = {}

        # Market maker quotes for at t
        quotes, cancellations = mm.update(ob, mm_notifications)

        # Market orders arrive for [t, t+1)
        market_orders = it.generate_orders(a.value, ob.mid_price, rng=rng)

        # The order book processes market maker requotes and orders for [t, t+1)
        ob.process_cancellations(cancellations)
        notifications = ob.process_orders(chain(quotes, market_orders))

        # Gathering market makers trade notifications
        mm_notifications = notifications[1] if 1 in notifications else []

        # Track trades and asset value
        for notif in mm_notifications:
            if notif.is_bid:
                for p, v in notif.price_volume.items():
                    bids_tick[p] = bids_tick.get(p, 0) + v
            else:
                for p, v in notif.price_volume.items():
                    asks_tick[p] = asks_tick.get(p, 0) + v
        bids.append(bids_tick)
        asks.append(asks_tick)
        asset_value.append(a.value)
        mid_price.append(ob.mid_price)

        # Evolve asset at t + 1 - eps
        a.evolve_value(rng=rng)

    # market maker summary statistics
    summary_stats = process_market_maker_data(mm)

    return {
        "bids": bids,
        "asks": asks,
        "asset value": asset_value,
        "mid price": mid_price,
        "mark-to-market": mm.history["mark-to-market"],
        "summary stats": summary_stats,
    }
