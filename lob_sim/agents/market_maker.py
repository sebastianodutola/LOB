"""
Market Maker Agent for LOB Simulation.

This module defines a market maker agent that quotes bid/ask orders based on
inventory position and exponentially smoothed mid-price. The market maker
processes trade notifications, tracks PnL, and uses a configurable strategy
function to generate orders.
"""


class MarketMaker:
    """
    Market maker agent that quotes bid/ask orders based on inventory and
    mid-price.

    The market maker maintains a single update cycle per tick that:
    1. Updates the exponentially-weighted moving average of mid-price
    2. Processes trade notifications from the previous tick
    3. Generates new quotes and cancels old ones
    4. Records historical data for analysis

    Attributes
    ----------
    trader_id : int
        Unique identifier for the trader.
    inventory : int
        Current inventory position (positive = long, negative = short).
    cash : float
        Cash balance. Increases on sells, decreases on buys.
    strategy : callable
        Strategy function that takes (inventory, mid_price) and returns
        a list of Order objects.
    EMA_mp : float
        Exponential moving average of mid-price.
    alpha : float
        EMA smoothing parameter (higher = more weight on recent prices).
    history : dict
        Dictionary containing historical time series data:
        - "mid price": list of mid-prices per tick
        - "inventory": list of inventory positions per tick
        - "cash": list of cash balances per tick
        - "buy volume": list of buy volumes per tick (incremental, not cumulative)
        - "sell volume": list of sell volumes per tick (incremental, not cumulative)
        - "mark-to-market": list of mark-to-market PnL
    Methods
    -------
    update(trades_notifications, order_book)
        Main update function called each tick to process state and generate quotes.
    get_stats()
        Get current inventory and cash statistics.
    """

    def __init__(self, strategy, alpha=0.13, trader_id=1):
        """
        Initialize the market maker with a trading strategy.

        Parameters
        ----------
        strategy : callable
            Strategy function with signature (inventory: int, mid_price: float) -> list[Order].
            Should return a list of Order objects representing the market maker's quotes.
        alpha : float, optional
            EMA smoothing parameter for mid-price. Higher values give more weight
            to recent observations. Default is 0.13 (approximately 5-tick half-life).
        trader_id : int, optional
            Id recognised by orderbook. Default is 1.
        """
        self.trader_id = trader_id
        self.inventory = 0
        self.cash = 0
        self.strategy = strategy
        # Mid-price smoothing
        self.EMA_mp = 100
        self.alpha = alpha  # EMA half life of 5 ticks

        # stats tracking
        self.history = {
            "mid price": [],
            "inventory": [],
            "cash": [],
            "buy volume": [],
            "sell volume": [],
            "spread": [],
            "mark-to-market": [],
        }

    def update(self, order_book, trades_notifications):
        """
        Update Market Maker state and generate new quotes for the current tick.

        This method is called once per simulation tick and performs the following steps:
        1. Updates mid-price EMA from the current order book
        2. Processes trade notifications from interval (t-1, t]
        3. Cancels all unfilled orders and generates new quotes via strategy
        4. Records current state to history

        Parameters
        ----------
        trades_notifications : list of TradesNotification
            List of trade notifications for fills that occurred in (t-1, t].
            Each notification contains information about filled orders for this trader.
        order_book : OrderBook
            Current state of the limit order book, used to extract mid-price
            and query unfilled orders.

        Returns
        -------
        quotes : list of Order
            List of new orders to submit to the order book.
        cancellations : list of int
            List of order IDs to cancel (all unfilled orders from previous tick).
        """
        # Update mid price
        mid_price = self._update_mid(order_book.mid_price)

        # Process trade notifications from (t-1, t]
        buy_volume, sell_volume = self._process_trades_notifications(
            trades_notifications
        )

        # Update Quotes
        unfilled_orders = order_book.unfilled_orders(self.trader_id)
        quotes, cancellations, spread = self._update_quotes(unfilled_orders)

        # Update History
        self.history["mid price"].append(mid_price)
        self.history["inventory"].append(self.inventory)
        self.history["cash"].append(self.cash)
        self.history["buy volume"].append(buy_volume)
        self.history["sell volume"].append(sell_volume)
        self.history["spread"].append(spread)

        # Update Pnl
        inventory_value = self.inventory * mid_price
        self.history["mark-to-market"].append(inventory_value + self.cash)

        # Return quotes and cancellations to be processed
        return quotes, cancellations

    def _update_quotes(self, unfilled_orders):
        """
        Generate new quotes via strategy and cancel all unfilled orders.

        Implements a "cancel-and-replace" approach where all outstanding orders
        are cancelled and replaced with fresh quotes each tick.

        Strategy dependent spread is also updated.

        Parameters
        ----------
        unfilled_orders : list of tuple
            List of (order_id, order) tuples representing unfilled orders
            for this trader.

        Returns
        -------
        quotes : list of Order
            List of new orders to submit, with trader_id set.
        cancellations : list of int
            List of order IDs to cancel.
        """
        # Generate orders via strategy
        quotes, spread = self.strategy(self.inventory, self.EMA_mp)
        for order in quotes:
            order.trader_id = self.trader_id
        cancellations = [unfilled_order[0] for unfilled_order in unfilled_orders]
        return quotes, cancellations, spread

    def _process_trades_notifications(self, trades_notifications):
        """
        Process trade notifications and update inventory and cash.

        Updates the market maker's position and cash based on filled orders,
        and returns the volume transacted in this tick for recording purposes.

        Parameters
        ----------
        trades_notifications : list of TradesNotification
            List of trade notifications for this trader.

        Returns
        -------
        buy_volume : int
            Total volume bought (filled on bid side) in this tick.
        sell_volume : int
            Total volume sold (filled on ask side) in this tick.

        Raises
        ------
        ValueError
            If a notification's trader_id doesn't match this market maker's trader_id.
        """
        buy_volume = 0
        sell_volume = 0
        for trades_notification in trades_notifications:
            if trades_notification.trader_id != self.trader_id:
                raise ValueError("Notification and trader don't match.")
            if trades_notification.is_bid:
                self.inventory += trades_notification.total_filled_volume
                self.cash -= trades_notification.total_notional
                buy_volume += trades_notification.total_filled_volume
            else:
                self.inventory -= trades_notification.total_filled_volume
                self.cash += trades_notification.total_notional
                sell_volume += trades_notification.total_filled_volume

        return buy_volume, sell_volume

    def _update_mid(self, current_mid, start_price=100):
        """
        Update exponential moving average of mid-price.

        Uses the current order book mid-price if available, otherwise falls back
        to the most recent historical mid-price or the starting price.

        Parameters
        ----------
        current_mid : float or None
            Current mid-price from order book. None if order book is empty.
        start_price : float, optional
            Initial mid-price to use if no history exists. Default is 100.

        Returns
        -------
        mid_price : float
            The mid-price to use for this tick (before EMA smoothing).
        """
        # Mid-price used is the most recent available book mid-price
        # Market maker has no knowledge of underlying value (except at t=0)
        if current_mid is not None:
            mid_price = current_mid
        elif len(self.history["mid price"]) == 0:
            mid_price = start_price
        else:
            mid_price = self.history["mid price"][-1]
        # EMA mid-price
        self.EMA_mp = self.alpha * mid_price + (1 - self.alpha) * self.EMA_mp
        return mid_price

    def get_stats(self):
        """
        Get current position and cash statistics.

        Returns
        -------
        dict
            Dictionary containing:
            - "Inventory": Current inventory position
            - "Cash": Current cash balance
        """
        return {"Inventory": self.inventory, "Cash": self.cash}
