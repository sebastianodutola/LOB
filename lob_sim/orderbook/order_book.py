"""
Limit order book with bid/ask matching and order expiration.

This module defines the OrderBook class that manages bid and ask sides,
processes incoming orders, handles cancellations, and tracks order lifetimes.
"""

from itertools import chain

from ..core import TradesNotification
from .expiration_wheel import ExpirationWheel
from .price_book import PriceBook


class OrderBook:
    """
    Central limit order book managing bids, asks, and order lifecycle.

    Attributes
    ----------
    bids : PriceBook
        Price book for the bid (buy) side.
    asks : PriceBook
        Price book for the ask (sell) side.
    expiration_wheel : ExpirationWheel
        Manages order expiration based on lifetime.
    trade_history : list of list
        History of [volume_traded, total_exchanged] for each batch.

    Methods
    -------
    spread
        Property returning bid-ask spread.
    mid_price
        Property returning mid-market price.
    Advance()
        Advance the book state by one timestep.
    get_best_bid()
        Get best bid price.
    get_best_ask()
        Get best ask price.
    process_orders(orders)
        Process incoming orders and return trade notifications.
    unfilled_orders(trader_id)
        Get all unfilled orders for a specific trader.
    process_cancellations(order_ids)
        Cancel orders by ID.
    get_bid_depth()
        Get total volume on bid side.
    get_ask_depth()
        Get total volume on ask side.
    display()
        Print readable view of both sides of the book.
    """

    def __init__(self, min_lifetime=3, max_lifetime=10_000):
        """
        Initialize an order book with expiration parameters.

        Parameters
        ----------
        min_lifetime : int, optional
            Default lifetime for orders without explicit lifetime (default is 3).
        max_lifetime : int, optional
            Maximum lifetime in time steps (default is 10,000).
        """
        self.bids = PriceBook(is_bid_side=True)
        self.asks = PriceBook(is_bid_side=False)
        self.expiration_wheel = ExpirationWheel(min_lifetime, max_lifetime)

        # History of volume traded and total money exchanged.
        self.trade_history = []

    @property
    def spread(self):
        """
        Calculate bid-ask spread.

        Returns
        -------
        float or None
            Spread between best ask and best bid, or None if either is missing.
        """
        if self.get_best_bid() is None or self.get_best_ask() is None:
            return None
        else:
            return round(self.get_best_ask() - self.get_best_bid(), 2)

    @property
    def mid_price(self):
        """
        Calculate mid-market price.

        Returns
        -------
        float or None
            Average of best bid and ask, or None if either is missing.
        """
        if self.get_best_bid() is None or self.get_best_ask() is None:
            return None
        else:
            return round((self.get_best_ask() + self.get_best_bid()) / 2, 2)
        
    def advance(self):
        """
        Advance the state of the book by one step, cancelling expiring orders.
        """
        expirations = self.expiration_wheel.advance()
        self.process_cancellations(expirations)

    def get_best_bid(self):
        """
        Get best bid price in the book.

        Returns
        -------
        float or None
            Highest bid price, or None if no bids.
        """
        return self.bids.get_best_price()

    def get_best_ask(self):
        """
        Get best ask price in the book.

        Returns
        -------
        float or None
            Lowest ask price, or None if no asks.
        """
        return self.asks.get_best_price()

    def process_orders(self, orders):
        """
        Process incoming orders, match trades, and add remaining to book.

        Parameters
        ----------
        orders : list of Order
            List of orders to process.

        Returns
        -------
        dict
            Dictionary mapping trader_id to list of TradesNotification objects.
        """
        trades = []
        for order in orders:
            if order.is_bid:
                trades.extend(self.asks.fill(order))
            else:
                trades.extend(self.bids.fill(order))

            # Only add remaining volume to book if it is a limit order
            if order.volume and not order.is_market:
                self.expiration_wheel.schedule(order)
                if order.is_bid:
                    self.bids.add(order)
                else:
                    self.asks.add(order)

        return self._process_trades(trades)

    def _process_trades(self, trades):
        """
        Aggregate trades into notifications and update history.

        Parameters
        ----------
        trades : list of Trade
            List of executed trades to process.

        Returns
        -------
        dict
            Dictionary mapping trader_id to list of TradesNotification objects.
        """
        volume_traded = 0
        total_exchanged = 0
        order_notifs = {}  # {order_id: TradesNotification}
        trader_notifs = {}  # {trader_id: [TradesNotification, ...]}

        for trade in trades:
            volume_traded += trade.volume
            total_exchanged += trade.price * trade.volume

            for order, trader_id in [(trade.bid_order, trade.bid_order.trader_id),
                                     (trade.ask_order, trade.ask_order.trader_id)]:
                if trader_id is not None:
                    # Update or create notification
                    if order.id not in order_notifs:
                        notif = TradesNotification(order)
                        order_notifs[order.id] = notif
                        trader_notifs.setdefault(trader_id, []).append(notif)

                    order_notifs[order.id].add_trade(trade)
                    # Updates trader_notifs too because stored notif is referenced
                    
        self.trade_history.append([volume_traded, total_exchanged])

        return trader_notifs  # Return trader-keyed version

    def unfilled_orders(self, trader_id):
        """
        Get all unfilled orders for a specific trader.

        Parameters
        ----------
        trader_id : int
            Identifier of the trader.

        Returns
        -------
        list of tuple
            List of (order_id, price, volume) tuples for unfilled orders.
        """
        unfilled_asks = self.asks.order_map.values()
        unfilled_bids = self.bids.order_map.values()
        unfilled_orders = [(order.id, order.price, order.volume)
                           for order in chain(unfilled_asks, unfilled_bids)
                           if order.trader_id == trader_id]
        return unfilled_orders

    def process_cancellations(self, order_ids):
        """
        Cancel orders by ID from either side of the book.

        Parameters
        ----------
        order_ids : list of int
            List of order IDs to cancel.
        """
        for order_id in order_ids:
            if order_id in self.bids.order_map:
                order = self.bids.order_map[order_id]
                self.bids.cancel(order)
            elif order_id in self.asks.order_map:
                order = self.asks.order_map[order_id]
                self.asks.cancel(order)
            else:
                # order not on books might have been filled.
                pass

    def get_bid_depth(self):
        """
        Get total volume on bid side of the book.

        Returns
        -------
        int
            Sum of all bid volumes across all price levels.
        """
        return self.bids.get_depth()

    def get_ask_depth(self):
        """
        Get total volume on ask side of the book.

        Returns
        -------
        int
            Sum of all ask volumes across all price levels.
        """
        return self.asks.get_depth()

    def __repr__(self):
        return (f"OrderBook(bids={self.bids.__repr__()}, "
                f"asks={self.asks.__repr__()})")

    def display(self):
        """
        Print readable view of both sides of the order book.
        """
        self.bids.display()
        self.asks.display()