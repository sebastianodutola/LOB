"""
Price level management for limit order book.

This module defines the PriceLevel class that maintains orders at a single
price point using a FIFO queue for order matching.
"""

from collections import deque

from ..core import Trade


class PriceLevel:
    """
    Maintains all orders at a specific price level with FIFO matching.

    Attributes
    ----------
    price : float
        The price level for this queue of orders.
    orders : deque
        FIFO queue of orders at this price level.
    volume : int
        Total volume of all orders at this price level.

    Methods
    -------
    add(order)
        Add an order to this price level.
    fill(order)
        Match incoming order against orders at this level.
    cancel(order)
        Remove a specific order from this price level.
    is_empty()
        Check if this price level has any orders.
    """

    def __init__(self, price):
        """
        Initialize a price level at the given price.

        Parameters
        ----------
        price : float
            The price level for this queue of orders.
        """
        self.price = price
        self.orders = deque()
        self.volume = 0

    def add(self, order):
        """
        Add an order to the end of the queue at this price level.

        Parameters
        ----------
        order : Order
            The order to add to this price level.
        """
        self.orders.append(order)
        self.volume += order.volume

    def _top(self):
        """
        Get the first order in the queue without removing it.

        Returns
        -------
        Order or None
            The first order in the queue, or None if empty.
        """
        if not self.orders:
            return None
        return self.orders[0]  # O(1)

    def _pop(self):
        """
        Remove and return the first order from the queue.

        Returns
        -------
        Order
            The first order in the queue.

        Raises
        ------
        IndexError
            If the price level is empty.
        """
        if not self.orders:
            raise IndexError("Price level is empty.")
        order = self.orders.popleft()  # O(1)
        self.volume -= order.volume
        return order

    def fill(self, order):
        """
        Match incoming order against orders at this price level.

        Parameters
        ----------
        order : Order
            The incoming order to fill against this price level.

        Returns
        -------
        trades : list of Trade
            List of executed trades.
        level_orders_filled : list of Order
            List of orders completely filled and removed from this level.
        """
        trades = []
        level_orders_filled = []
        is_bid = order.is_bid

        while not self.is_empty() and order.volume > 0:
            top_order = self._top()

            if top_order.volume > order.volume:
                trade_volume = order.volume

            elif top_order.volume == order.volume:
                trade_volume = order.volume
                level_orders_filled.append(self._pop())

            else:
                trade_volume = top_order.volume
                level_orders_filled.append(self._pop())

            # Update order volumes
            top_order.volume -= trade_volume
            order.volume -= trade_volume
            self.volume -= trade_volume

            # Log trade
            bid = order if is_bid else top_order
            ask = top_order if is_bid else order
            trade = Trade(bid, ask, self.price, trade_volume)
            trades.append(trade)

        return trades, level_orders_filled

    def cancel(self, order):
        """
        Remove a specific order from this price level.

        Parameters
        ----------
        order : Order
            The order to remove from this price level.

        Raises
        ------
        ValueError
            If the order is not found at this price level.
        """
        try:
            self.orders.remove(order)  # O(n)
        except ValueError:
            raise ValueError("Order not found at this price level.")
        self.volume -= order.volume

    def is_empty(self):
        """
        Check if this price level has any orders.

        Returns
        -------
        bool
            True if no orders remain, False otherwise.
        """
        return True if len(self.orders) == 0 else False

    def __repr__(self):
        return f"PriceLevel(price={self.price}, orders={list(self.orders)})"

    def __str__(self):
        volume = sum(order.volume for order in self.orders)
        return (f"PriceLevel: Price={self.price}, Volume={volume}, "
                f"Orders={len(self.orders)}")
