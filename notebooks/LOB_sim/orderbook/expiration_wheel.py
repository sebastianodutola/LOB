"""
Expiration wheel for efficient order lifetime management.

This module implements a circular buffer-based expiration system for
orders with time-to-live (TTL) constraints.
"""


class ExpirationWheel:
    """
    Circular buffer for tracking and expiring orders by lifetime.

    Uses a fixed-size circular buffer where each bucket holds orders
    expiring at that time step. Time advances cyclically through buckets.

    Attributes
    ----------
    max_lifetime : int
        Maximum lifetime (in time steps) for any order.
    min_lifetime : int
        Default lifetime assigned to orders without explicit lifetime.
    expiration_bucket : list of list
        Circular buffer where each bucket contains order IDs expiring at
        that time step.
    now : int
        Current time step (index into expiration_bucket).

    Methods
    -------
    schedule(order)
        Schedule an order for expiration based on its lifetime.
    advance()
        Advance time by one step and return expired order IDs.
    """

    def __init__(self, min_lifetime, max_lifetime):
        """
        Initialize the expiration wheel with lifetime bounds.

        Parameters
        ----------
        min_lifetime : int
            Default lifetime assigned to orders without explicit lifetime.
        max_lifetime : int
            Maximum lifetime (in time steps) for any order.
        """
        self.max_lifetime = max_lifetime
        self.min_lifetime = min_lifetime
        self.expiration_bucket = [[] for _ in range(max_lifetime)]
        self.now = 0

    def schedule(self, order):
        """
        Schedule an order for expiration based on its lifetime.

        Parameters
        ----------
        order : Order
            The order to schedule, with optional lifetime attribute.
        """
        lifetime = (order.lifetime if order.lifetime is not None
                    else self.min_lifetime)
        expiration = (self.now + lifetime) % self.max_lifetime
        self.expiration_bucket[expiration].append(order.id)

    def advance(self):
        """
        Advance time by one step and return expired order IDs.

        Returns
        -------
        list of int
            List of order IDs that expired at the current time step.
        """
        self.now = (self.now + 1) % self.max_lifetime
        expired = self.expiration_bucket[self.now]
        self.expiration_bucket[self.now] = []
        return expired