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

    Attributes
    ----------
    trader_id : int
        Unique identifier for the trader.
    inventory : int
        Current inventory position.
    cash : float
        Cash balance.
    strategy : callable
        Strategy function that generates orders.
    EMA_mp : float
        Exponential moving average of mid-price.
    alpha : float
        EMA smoothing parameter.
    mp_history : list
        History of mid-prices.
    pnl_history : list
        History of PnL values.
    buy_volume : int
        Cumulative buy volume.
    sell_volume : int
        Cumulative sell volume.

    Methods
    -------
    order_update(order_book)
        Generate orders and cancellations based on current order book.
    process_trades_notifications(trades_notifications)
        Process trade notifications and update inventory, cash, and volume.
    update_mid(current_mid)
        Update mid-price history and EMA.
    update_pnl()
        Calculate and record mark-to-market PnL.
    get_stats()
        Get current inventory and cash statistics.
    """

    def __init__(self, strategy, alpha=0.13):
        """
        Parameters
        ----------
        strategy : callable
            Strategy function that takes (inventory, mid_price) and returns
            orders.
        alpha : float, optional
            EMA smoothing parameter. Default is 0.13.
        """
        self.trader_id = 1
        self.inventory = 0
        self.cash = 0
        self.strategy = strategy
        # Mid-price smoothing
        self.EMA_mp = 100
        self.alpha = alpha  # EMA half life of 5 ticks
        self.mp_history = []
        # PnL tracking
        self.pnl_history = []
        self.buy_volume = 0
        self.sell_volume = 0

    def order_update(self, order_book):
        """
        Generate orders and cancellations based on current order book.

        Parameters
        ----------
        order_book : OrderBook
            Current state of the order book.

        Returns
        -------
        orders : list
            List of new orders to submit.
        cancellations : list
            List of order IDs to cancel.
        """
        # Update mid
        self.update_mid(order_book.mid_price)
        # Generate orders via strategy
        orders = self.strategy(self.inventory, self.EMA_mp)
        for order in orders:
            order.trader_id = self.trader_id
        cancellations = [unfilled_order[0] for unfilled_order in
                         order_book.unfilled_orders(self.trader_id)]
        return orders, cancellations

    def process_trades_notifications(self, trades_notifications):
        """
        Process trade notifications and update inventory, cash, and volume.

        Parameters
        ----------
        trades_notifications : list
            List of trade notification objects.
        """
        for trades_notification in trades_notifications:
            if trades_notification.trader_id != self.trader_id:
                raise ValueError("Notification and trader don't match.")
            if trades_notification.is_bid:
                self.inventory += trades_notification.total_filled_volume
                self.cash -= trades_notification.total_notional
                self.buy_volume += trades_notification.total_filled_volume
            else:
                self.inventory -= trades_notification.total_filled_volume
                self.cash += trades_notification.total_notional
                self.sell_volume += trades_notification.total_filled_volume

    def update_mid(self, current_mid, start_price):
        """
        Update mid-price history and EMA.

        Parameters
        ----------
        current_mid : float or None
            Current mid-price from order book.
        """
        # Mid-price used is the most recent available book mid-price
        # Market maker has no knowledge of underlying value (except at t=0)
        if current_mid is not None:
            mid_price = current_mid
        elif len(self.mp_history) == 0:
            mid_price = start_price
        else:
            mid_price = self.mp_history[-1]
        self.mp_history.append(mid_price)
        # EMA mid-price
        self.EMA_mp = self.alpha * mid_price + (1 - self.alpha) * self.EMA_mp

    def update_pnl(self):
        """
        Calculate and record mark-to-market PnL.

        Returns
        -------
        total_pnl : float or None
            Total PnL (cash + unrealized).
        """
        # Mark to market
        if self.mp_history:
            unrealised_pnl = self.mp_history[-1] * self.inventory
            total_pnl = self.cash + unrealised_pnl
            self.pnl_history.append(total_pnl)
            return total_pnl
        else:
            return 0

    def get_stats(self):
        """
        Get current inventory and cash statistics.

        Returns
        -------
        dict
            Dictionary with inventory and cash values.
        """
        return {
            "Inventory": self.inventory,
            "Cash": self.cash
        }