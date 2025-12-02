"""
Informed trader agent that generates market orders based on asset mispricing.
"""

import numpy as np
from ..core import MarketOrder


class InformedTraders:
    """
    Informed trader agent that generates market orders correlated with price mispricing.

    Attributes
    ----------
    information_coeff : float
        Information coefficient in [0, 1] controlling correlation between order
        direction and mispricing. 0 = uninformed (50/50), 1 = fully informed
        (always trades in correct direction).
    arrival_rate : float
        Mean number of order arrivals per tick (Poisson rate parameter).
    max_volume : int
        Maximum volume for any single market order.

    Methods
    -------
    generate_orders(asset_value, mid_price, rng=None)
        Generate market orders for the current tick based on mispricing.
    """

    def __init__(self, information_coeff, arrival_rate, max_volume):
        """
        Initialize the informed trader agent with bounds checking.

        Parameters
        ----------
        information_coeff : float
            Information coefficient in [0, 1]. Higher values mean stronger
            correlation between order direction and price mispricing.
        arrival_rate : float
            Mean number of orders per tick (must be positive).
        max_volume : int
            Maximum volume for any single market order (must be positive).

        Raises
        ------
        ValueError
            If information_coeff not in [0, 1], or if arrival_rate or max_volume
            are not positive.
        """
        if not 0 <= information_coeff <= 1:
            raise ValueError(
                f"information_coeff must be in [0, 1], got {information_coeff}"
            )
        if arrival_rate <= 0:
            raise ValueError(f"arrival_rate must be positive, got {arrival_rate}")
        if max_volume <= 0:
            raise ValueError(f"max_volume must be positive, got {max_volume}")

        self.information_coeff = information_coeff
        self.arrival_rate = arrival_rate
        self.max_volume = max_volume

    def __repr__(self):
        return (
            f"InformedTraders(information_coeff={self.information_coeff}, "
            f"arrival_rate={self.arrival_rate}, max_volume={self.max_volume})"
        )

    def generate_orders(self, asset_value, mid_price, rng=None):
        """
        Generate market orders with Poisson arrivals biased toward mispricing direction.

        Parameters
        ----------
        asset_value : float
            True value of the asset.
        mid_price : float or None
            Current market mid-price. If None, orders are generated with no
            directional bias (50/50 buy/sell).
        rng : numpy.random.Generator, optional
            Random number generator for reproducibility. If None, creates a new
            unseeded generator.

        Returns
        -------
        list of MarketOrder
            List of market orders to submit this tick. Each order has a volume,
            direction (is_bid), and trader_id of 0.
        """
        rng = rng if rng is not None else np.random.default_rng()

        num_orders = rng.poisson(self.arrival_rate)
        volume = rng.integers(1, self.max_volume + 1, num_orders)
        trade_direction = (
            np.sign((asset_value - mid_price)) if mid_price is not None else 0
        )
        bid_prob = 0.5 + 0.5 * trade_direction * self.information_coeff
        is_bid = rng.random(num_orders) < bid_prob

        return [MarketOrder(v, b, 0) for v, b in zip(volume, is_bid)]
