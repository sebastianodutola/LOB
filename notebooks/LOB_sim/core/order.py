"""
Order and market order classes for trading simulation.

This module defines order types used in limit order book,
including limit orders and market orders with tracking capabilities.
"""


class Order:
    """
    Represents a limit or market order with price, volume, and side.

    Attributes
    ----------
    price : float or None
        Limit price for the order (None for some order types).
    volume : int
        Quantity of shares or contracts in the order.
    is_bid : bool
        True if buy order, False if sell order.
    id : int
        Unique identifier for this order.
    is_market : bool
        True if market order, False if limit order.
    trader_id : int or None
        Identifier of the trader placing the order.
    lifetime : int or None
        Number of time steps the order remains active.
    """

    _id_counter = 0

    def __init__(self, price=None, volume=100, is_bid=True, is_market=False,
                 trader_id=None, lifetime=None):
        """
        Initialize an order with specified parameters.

        Parameters
        ----------
        price : float or None, optional
            Limit price for the order (default is None).
        volume : int, optional
            Quantity of shares or contracts (default is 100).
        is_bid : bool, optional
            True for buy order, False for sell order (default is True).
        is_market : bool, optional
            True for market order, False for limit order (default is False).
        trader_id : int or None, optional
            Identifier of the trader placing the order (default is None).
        lifetime : int or None, optional
            Number of time steps order remains active (default is None).
        """
        self.price = price
        self.volume = volume
        self.is_bid = is_bid
        self.id = Order._id_counter
        self.is_market = is_market
        self.trader_id = trader_id
        self.lifetime = lifetime

        Order._id_counter += 1

    def __repr__(self):
        side = "BID" if self.is_bid else "ASK"
        type_ = "MARKET" if self.is_market else "LIMIT"
        return (f"Order(id={self.id}, price={self.price}, volume={self.volume}, "
                f"side={side}, type={type_}, trader_id={self.trader_id})")


class MarketOrder(Order):
    """
    Market order that executes immediately at best available price.

    Market orders have infinite price in the direction of the trade
    to ensure immediate execution against the order book.

    Attributes
    ----------
    Inherits all attributes from Order class.
    """

    def __init__(self, volume=100, is_bid=True, trader_id=None):
        """
        Initialize a market order with specified parameters.

        Parameters
        ----------
        volume : int, optional
            Quantity of shares or contracts (default is 100).
        is_bid : bool, optional
            True for buy order, False for sell order (default is True).
        trader_id : int or None, optional
            Identifier of the trader placing the order (default is None).
        """
        price = float('inf') if is_bid else -float('inf')
        super().__init__(price, volume, is_bid, is_market=True,
                         trader_id=trader_id)