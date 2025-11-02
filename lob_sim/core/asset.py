"""
Asset Class for LOB simulation.
This module defines an asset with value evolving as a random walk.
"""
import numpy as np


class Asset:
    """
    Asset with value evolving as a random walk.

    Attributes
    ----------
    initial_value : float
        Starting value of the asset.
    value : float
        Current value of the asset.
    
    Methods
    -------
    evolve_value()
        update asset value.
    """
    
    def __init__(self, initial_value=100):
        """
        Parameters
        ----------
        initial_value : float, optional
            Starting value of the asset. Default is 100.
        """
        self.initial_value = initial_value
        self.value = initial_value

    def evolve_value(self, drift=0, sigma=0.5, rng=None):
        """
        Update asset value with random walk step.

        Parameters
        ----------
        drift : float, optional
            Mean of the normal distribution. Default is 0.
        sigma : float, optional
            Standard deviation of the normal distribution. Default is 0.5.
        rng : np.random.Generator, optional
            Random number generator.
        """
        if rng is None:
            rng = np.random.default_rng()
        self.value += rng.normal(drift, sigma)

    def __repr__(self):
        return f"Asset(value={self.value})"

    def __str__(self):
        """
        Returns
        -------
        str
            Human-readable string describing the asset.
        """
        return (f"Current Value: {self.value}, "
                f"Initial Value: {self.initial_value}")