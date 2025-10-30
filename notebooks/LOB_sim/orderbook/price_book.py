"""
Price book management using heap-based price level ordering.

This module defines the PriceBook class that maintains price levels for
one side of the order book (bid or ask) using a heap for efficient
best price retrieval.
"""

import heapq as hq

from .price_level import PriceLevel


class PriceBook:
    """
    Manages all price levels on one side of the order book.

    Uses a heap to efficiently track the best price and a dictionary
    to store price levels. Bid side uses max-heap via negative prices.

    Attributes
    ----------
    order_map : dict
        Maps order IDs to order objects for fast lookup.
    is_bid_side : bool
        True if this is the bid (buy) side, False for ask (sell) side.

    Methods
    -------
    add(order)
        Add an order to the appropriate price level.
    cancel(order)
        Cancel and remove an order from the book.
    best_price()
        Get the best available price on this side.
    fill(order)
        Fill an incoming order against this side of the book.
    volume()
        Get total volume across all price levels.
    display()
        Print a readable view of all price levels.
    """

    def __init__(self, is_bid_side):
        """
        Initialize a price book for one side of the market.

        Parameters
        ----------
        is_bid_side : bool
            True if this is the bid (buy) side, False for ask (sell) side.
        """
        self.order_map = {}
        self._price_levels = {}
        self._heap = []
        self.is_bid_side = is_bid_side

    def add(self, order):
        """
        Add an order to the appropriate price level.

        Parameters
        ----------
        order : Order
            The order to add to the book.
        """
        price = order.price

        if price not in self._price_levels:
            # Add price level to heap
            self._price_levels[price] = PriceLevel(price)
            # Use negative price for max-heap behavior on bid side.
            heap_price = -price if self.is_bid_side else price
            hq.heappush(self._heap, heap_price)

        # Add order to price level
        self._price_levels[price].add(order)
        # Add order to the order map
        self.order_map[order.id] = order

    def cancel(self, order):
        """
        Cancel and remove an order from the book.

        Parameters
        ----------
        order : Order
            The order to cancel and remove.

        Raises
        ------
        ValueError
            If the price or order is not found in the book.
        """
        price = order.price
        if price not in self._price_levels:
            raise ValueError(f"Price {price} not found in PriceBook.")

        try:
            self._price_levels[price].cancel(order)
            # Trying to remove the price level from the heap here would be
            # O(N) so we delay clean up
        except ValueError as e:
            # Propagate the original error
            raise ValueError(f"Failed to cancel order {order.id}: {e}") from e

        # Remove from order map
        del self.order_map[order.id]

    def get_best_price(self):
        """
        Get the best available price on this side of the book.

        Returns
        -------
        float or None
            The best price, or None if the book is empty.
        
        Notes
        -----
        This method also performs internal cleanup by removing empty price levels
        from the bid heap. As a result, it may modify internal state.
        """
        if not self._price_levels:
            return None
        else:
            # Since I didn't remove empty price levels upon order cancellation
            # I have to handle it here
            while self._heap:
                best_price = -self._heap[0] if self.is_bid_side else self._heap[0]
                # Remove empty price levels
                if self._price_levels[best_price].is_empty():
                    hq.heappop(self._heap)
                    del self._price_levels[best_price]
                else:
                    break

            if self._heap:
                return best_price
            else:
                return None

    def fill(self, order):
        """
        Fill an incoming order against this side of the book.

        Parameters
        ----------
        order : Order
            The incoming order to fill.

        Returns
        -------
        list of Trade
            List of executed trades resulting from the fill.

        Raises
        ------
        ValueError
            If the order is on the same side as this book.
        KeyError
            If an order ID is not found in the order map.
        """
        if order.is_bid == self.is_bid_side:
            raise ValueError(
                "Cannot fill an order on the same side of the PriceBook."
            )

        price = order.price
        trades = []
        best_price = self.best_price()

        while best_price and order.volume > 0:

            # Check whether prices are compatible
            can_fill = (best_price >= price) if self.is_bid_side else (
                best_price <= price
            )

            if can_fill:
                trades_at_price, orders_filled = self._price_levels[
                    best_price
                ].fill(order)
                trades.extend(trades_at_price)
                for o in orders_filled:
                    try:
                        del self.order_map[o.id]
                    except KeyError as e:
                        raise KeyError(
                            f"Tried to delete order {e} from the order_map. "
                            f"It is probably a duplicate order."
                        )

            else:
                break

            # This simultaneously removes empty price levels and establishes
            # next best_price
            best_price = self.best_price()

        # Return list of trades
        return trades

    def get_depth(self):
        """
        Get depth, the total volume across all price levels.

        Returns
        -------
        int
            Sum of volumes at all price levels.
        """
        return sum(level.volume for level in self._price_levels.values())

    def __repr__(self):
        return (f"PriceBook(is_bid_side={self.is_bid_side}, "
                f"price_levels={sorted(list(self._price_levels.keys()))})")

    def display(self):
        """
        Print a readable view of all price levels in the book.
        """
        print(f"{'BID' if self.is_bid_side else 'ASK'} PriceBook:")
        for heap_price in sorted(self._heap, reverse=not self.is_bid_side):
            price = -heap_price if self.is_bid_side else heap_price
            price_level = self._price_levels[price]
            print(price_level)