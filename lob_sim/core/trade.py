"""
Trade class for recording executed transactions in trading simulation.

This module defines the Trade class that captures bid-ask matches
with price and volume information, and TradesNotification for
aggregating fill information.
"""


class Trade:
    """
    Represents an executed trade between a bid and ask order.

    Attributes
    ----------
    bid_order : Order
        The buy order involved in the trade.
    ask_order : Order
        The sell order involved in the trade.
    price : float
        Execution price of the trade.
    volume : int
        Quantity of shares or contracts traded.

    Methods
    -------
    __repr__()
        Return string representation of the trade.
    """

    def __init__(self, bid_order, ask_order, price, volume):
        """
        Initialize a trade with bid, ask, price, and volume.

        Parameters
        ----------
        bid_order : Order
            The buy order involved in the trade.
        ask_order : Order
            The sell order involved in the trade.
        price : float
            Execution price of the trade.
        volume : int
            Quantity of shares or contracts traded.
        """
        self.bid_order = bid_order
        self.ask_order = ask_order
        self.price = price
        self.volume = volume

    def __repr__(self):
        return (f"Trade(bid_id={self.bid_order.id}, ask_id={self.ask_order.id}, "
                f"price={self.price}, volume={self.volume})")


class TradesNotification:
    """
    Aggregates fill information for an order across multiple trades.

    Attributes
    ----------
    trader_id : int or None
        Identifier of the trader who placed the order.
    order_id : int
        Unique identifier of the order.
    is_bid : bool
        True if buy order, False if sell order.
    price_volume : dict
        Maps execution prices to total volume filled at each price.
    num_trades : int
        Count of trades executed for this order.
    total_filled_volume : int
        Total volume filled across all trades.
    total_notional : float
        Total value of all fills (sum of price * volume).
    remaining_volume : int
        Volume remaining unfilled from the original order.
    is_filled : bool
        True if order is completely filled, False otherwise.

    Methods
    -------
    average_price
        Property returning volume-weighted average fill price.
    add_trade(trade)
        Add a trade to this notification and update statistics.
    """

    def __init__(self, order):
        """
        Initialize a trades notification from an order.

        Parameters
        ----------
        order : Order
            The order for which to track fill information.
        """
        self.trader_id = order.trader_id
        self.order_id = order.id
        self.is_bid = order.is_bid

        self.price_volume = {}
        self.num_trades = 0

        self.total_filled_volume = 0
        self.total_notional = 0.0

        self.remaining_volume = order.volume
        self.is_filled = order.volume == 0

    @property
    def average_price(self):
        """
        Calculate volume-weighted average fill price.

        Returns
        -------
        float
            Average price across all fills.
        """
        if self.total_filled_volume > 0:
            return self.total_notional / self.total_filled_volume
        return 0

    def add_trade(self, trade):
        """
        Add a trade to this notification and update statistics.

        Parameters
        ----------
        trade : Trade
            The trade to add to this notification.

        Returns
        -------
        TradesNotification
            Returns self for method chaining.
        """
        self.price_volume[trade.price] = (
            self.price_volume.get(trade.price, 0) + trade.volume
        )
        self.num_trades += 1
        self.total_filled_volume += trade.volume
        self.total_notional += trade.price * trade.volume
        return self

    def __repr__(self):
        status = "FILLED" if self.is_filled else "PARTIAL"
        return (f"TradesNotification(order_id={self.order_id}, "
                f"filled {self.total_filled_volume}@{self.average_price:.2f} avg, "
                f"{self.num_trades} trades, remaining={self.remaining_volume}, "
                f"{status})")

    def __str__(self):
        status = "FILLED \u2713" if self.is_filled else "PARTIAL"
        return (f"order_id:{self.order_id}, \n"
                f"filled {self.total_filled_volume}@{self.average_price:.2f} avg, \n"
                f"{self.num_trades} trades, remaining:{self.remaining_volume}, "
                f"{status}")