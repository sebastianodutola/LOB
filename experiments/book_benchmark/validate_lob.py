"""
Demonstration of limit order book performance and correctness.

This script validates the LOB implementation by testing the core functionality with a tractable example.

Run with:
    python validate LOB

Expected output:
    - functionality validation (book state snapshots and validation messages)
"""

from math import isclose

from lob.orderbook import OrderBook
from lob.core import Order, MarketOrder


def run_validation():
    # Create a simple OrderBook
    ob = OrderBook(use_scheduler=True)

    # Reset Order ID counter
    Order._id_counter = 1

    # Add some test orders
    orders = [
        Order(
            trader_id=101,
            price=100,
            volume=10,
            is_bid=True,
            is_market=False,
            lifetime=1,
        ),
        Order(trader_id=101, price=101, volume=5, is_bid=True, is_market=False),
        Order(trader_id=201, price=102, volume=7, is_bid=False, is_market=False),
        Order(trader_id=202, price=103, volume=8, is_bid=False, is_market=False),
    ]

    ob.process_orders(orders)

    # Validate best bid/ask
    assert ob.get_best_bid() == 101
    assert ob.get_best_ask() == 102
    print("✅ Best bid/ask validated!")
    print(f"Order Book Status at Checkpoint 1:")
    ob.display()
    # ==== Checkpoint 1 ====

    # Validate unfilled orders for a trader
    trader_101_orders = ob.unfilled_orders(101)
    trader_201_orders = ob.unfilled_orders(201)
    assert trader_101_orders[0] == (1, 100, 10)
    assert trader_201_orders[0] == (3, 102, 7)
    print("✅ unfilled orders validated")

    # Validate spread and mid-price cancellation
    assert isclose(ob.mid_price, 101.5)
    assert isclose(ob.spread, 1.0)
    print("✅ Spread and mid-price validated")

    # Validate market-order trade and bid_depth logic
    mo = MarketOrder(trader_id=203, volume=8, is_bid=False)
    ob.process_orders([mo])
    assert ob.get_best_bid() == 100
    assert ob.get_bid_depth() == 7
    print("✅ Market-order trade and bid_depth logic validated")
    print(f"Order Book Status at Checkpoint 2:")
    ob.display()
    # ==== Checkpoint 2 ====

    # Validate cancellations
    ob.process_cancellations([4])
    assert ob.get_ask_depth() == 7
    print("✅ Cancellations validated")

    # Validate expiry
    ob.advance()
    assert ob.get_best_bid() == None
    print("✅ Expiry validated")
    print(f"Order Book Status at Checkpoint 3:")
    ob.display()
    # ==== Checkpoint 3 ====

    # Validate Clearing
    ob.clear()
    assert ob.get_ask_depth() == 0
    print("✅ Clearing validated")
    print(f"Order Book Status at Checkpoint 4:")
    ob.display()
    # ==== Checkpoint 4 ====


if __name__ == "__main__":
    run_validation()
