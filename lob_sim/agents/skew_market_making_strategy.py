"""
Skew Market Making Strategy for LOB Simulation.

This module defines a market making strategy that adjusts bid/ask quotes based
on inventory exposure, shifting prices to manage risk.
"""

from ..core import Order


class SkewMarketMakingStrategy:
    """
    Market making strategy with inventory-based price skew.

    Attributes
    ----------
    size : float
        Order size for each quote.
    spread : float
        Bid-ask spread.
    exposure_limit : float
        Maximum absolute exposure (inventory * mid_price).
    skew_coefficient : float
        Coefficient controlling skew magnitude.

    Methods
    -------
    __call__(inventory, mid_price)
        Generate bid/ask orders with inventory-based skew.
    """

    def __init__(self, spread, size, exposure_limit, skew_coefficient=1e-4):
        """
        Parameters
        ----------
        spread : float
            Bid-ask spread.
        size : float
            Order size for each quote.
        exposure_limit : float
            Maximum absolute exposure (inventory * mid_price).
        skew_coefficient : float, optional
            Coefficient controlling skew magnitude. Default is 1e-4.
        """
        self.size = size
        self.spread = spread
        self.exposure_limit = exposure_limit
        self.skew_coefficient = skew_coefficient

    def __call__(self, inventory, mid_price):
        """
        Generate bid/ask orders with inventory-based skew.

        Parameters
        ----------
        inventory : float
            Current inventory position.
        mid_price : float
            Current mid-price.

        Returns
        -------
        list
            List of Order objects.
        float
            Current spread.
        """
        orders = []
        exposure = inventory * mid_price
        skew = exposure * self.skew_coefficient
        # Skew is proportional to inventory
        if exposure <= self.exposure_limit:
            orders.append(
                Order(mid_price - self.spread / 2 - skew, self.size, True, False)
            )
        if exposure >= -self.exposure_limit:
            orders.append(
                Order(mid_price + self.spread / 2 - skew, self.size, False, False)
            )
        # Bubble spread for tracking purposes
        return orders, self.spread
