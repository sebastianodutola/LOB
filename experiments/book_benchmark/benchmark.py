import timeit
import random
import sys
import cProfile
import pstats
from lob.orderbook import OrderBook
from lob.core import Order

# --- 1. Benchmark Configuration ---

# Reproducibility
RANDOM_SEED = 42

# Book configuration
TOTAL_LIMIT_ORDERS = 1_000_000

# Workload configuration
ADD_RUNS = 10  # Number of times to add TOTAL_LIMIT_ORDERS
MARKET_ORDER_COUNT = 10_000
MARKET_ORDER_QTY = 150
MATCH_RUNS = 10  # Number of times to match MARKET_ORDER_COUNT orders

CANCEL_BATCH_SIZE = 1_000
CANCEL_RUNS = 100  # Number of times to cancel CANCEL_BATCH_SIZE orders
# Total cancellations benchmarked = 100 * 1,000 = 100,000

# --- 2. Scenarios to Test ---
# This directly tests your O(n) hypothesis.
# We vary the number of price levels to control the number of orders per level.
SCENARIOS = {
    "ShallowBook": {
        "num_levels": 100_000,  # 1M orders / 100k levels = ~10 orders/level
        "desc": "(~10 orders/level)",
    },
    "DeepBook": {
        "num_levels": 100,  # 1M orders / 100 levels = ~10,000 orders/level
        "desc": "(~10k orders/level)",
    },
}

# --- 3. Setup String Templates ---


# Setup for adding limit orders
def get_setup_add(num_levels):
    return f"""
from lob.orderbook import OrderBook
from lob.core import Order
import random
random.seed({RANDOM_SEED})

ob = OrderBook()
orders = []
for i in range({TOTAL_LIMIT_ORDERS}):
    # {num_levels} levels -> approx {TOTAL_LIMIT_ORDERS / num_levels:.0f} orders/level
    orders.append(Order(price=100 + (i % {num_levels}), volume=100, is_bid=True))

# Shuffle to make insertion non-sequential
random.shuffle(orders)
"""


STMT_ADD = """
ob.process_orders(orders)
ob.clear()
"""


# Setup for matching market orders
def get_setup_match(num_levels):
    return f"""
from lob.orderbook import OrderBook
from lob.core import Order, MarketOrder
import random
random.seed({RANDOM_SEED})

ob = OrderBook()
book_orders = []
# Build the book with limit orders
for i in range({TOTAL_LIMIT_ORDERS}):
    book_orders.append(Order(price=100 + (i % {num_levels}), volume=100, is_bid=True)) # Bids
ob.process_orders(book_orders)

# Create market orders to match against the book
market_orders = []
for i in range({MARKET_ORDER_COUNT}):
    market_orders.append(MarketOrder(volume={MARKET_ORDER_QTY}, is_bid=False)) # Asks (to match bids)
"""


STMT_MATCH = """
ob.process_orders(market_orders)
"""


# Setup for cancelling orders
def get_setup_cancel(num_levels):
    total_to_cancel = CANCEL_BATCH_SIZE * CANCEL_RUNS
    return f"""
from lob.orderbook import OrderBook
from lob.core import Order
import random
random.seed({RANDOM_SEED})

ob = OrderBook()
orders = []
order_ids = []
# Build the book
for i in range({TOTAL_LIMIT_ORDERS}):
    order = Order(price=100 + (i % {num_levels}), volume=100, is_bid=True)
    orders.append(order)
    order_ids.append(order.id)
ob.process_orders(orders)

# Shuffle IDs to ensure random cancellation across levels
random.shuffle(order_ids)

# Create batches for cancellation
cancellation_batches = [order_ids[i: i + {CANCEL_BATCH_SIZE}] for i in range(0, {total_to_cancel}, {CANCEL_BATCH_SIZE})]
num_batches = len(cancellation_batches)
batch_idx = 0
"""


STMT_CANCEL = f"""
ob.process_cancellations(cancellation_batches[batch_idx])
batch_idx = (batch_idx + 1) % num_batches
"""


# --- 4. Profiling Functions ---


def profile_operation(
    stream=sys.stdout, scenario="DeepBook", profile_type="Additions", num_stats=5
):
    """
    Runs cProfile on a specific scenario and operation type.

    Args:
        stream: The stream to write pstats output to (e.g., sys.stdout).
        scenario (str): The key from the SCENARIOS dict (e.g., "ShallowBook").
        profile_type (str): The operation to profile ("Additions" or "Cancellations").
        num_stats (int): The number of lines to print from the profiler.
    """

    # 1. Common Setup
    pr = cProfile.Profile()
    random.seed(RANDOM_SEED)
    ob = OrderBook()
    orders = []
    num_levels = SCENARIOS[scenario]["num_levels"]

    # 2. Specific Setup & Action based on profile_type
    if profile_type == "Additions":
        stream.write(f"Profiling 1 run of adding {TOTAL_LIMIT_ORDERS} orders...\n\n")

        # Setup for Add
        for i in range(TOTAL_LIMIT_ORDERS):
            # Using your new keywords 'volume' and 'is_bid'
            orders.append(Order(price=100 + (i % num_levels), volume=100, is_bid=True))
        random.shuffle(orders)

        # Action for Add
        pr.enable()
        ob.process_orders(orders)
        pr.disable()

    elif profile_type == "Cancellations":
        stream.write(
            f"Profiling {CANCEL_RUNS} batches of {CANCEL_BATCH_SIZE} cancellations...\n\n"
        )

        # Setup for Cancel
        order_ids = []
        for i in range(TOTAL_LIMIT_ORDERS):
            order = Order(price=100 + (i % num_levels), volume=100, is_bid=True)
            orders.append(order)
            order_ids.append(order.id)
        ob.process_orders(orders)
        random.shuffle(order_ids)

        total_to_cancel = CANCEL_BATCH_SIZE * CANCEL_RUNS
        cancellation_batches = [
            order_ids[i : i + CANCEL_BATCH_SIZE]
            for i in range(0, total_to_cancel, CANCEL_BATCH_SIZE)
        ]

        # Action for Cancel
        pr.enable()
        for i in range(CANCEL_RUNS):
            ob.process_cancellations(cancellation_batches[i])
        pr.disable()

    else:
        stream.write(f"Error: Unknown profile_type '{profile_type}'\n")
        return

    # 3. Common Reporting (Truncated to 5 as requested)
    stats = pstats.Stats(pr, stream=stream).sort_stats(pstats.SortKey.CUMULATIVE)
    stats.print_stats(num_stats)


# --- 5. Main Execution ---


def run_benchmarks():
    """Runs all timeit benchmarks and prints a formatted table."""

    print("Running Order Book Benchmarks...")
    print(f"Seed: {RANDOM_SEED}, Total Limit Orders: {TOTAL_LIMIT_ORDERS}")
    print("-" * 70)

    results = []

    for scenario_name, config in SCENARIOS.items():
        num_levels = config["num_levels"]
        desc = config["desc"]
        print(f"\nTesting Scenario: {scenario_name} {desc}")

        # --- Add Orders Benchmark ---
        print(f"  Running Add... ({ADD_RUNS} runs of {TOTAL_LIMIT_ORDERS} orders)")
        setup_add = get_setup_add(num_levels)
        time_add = timeit.timeit(setup=setup_add, stmt=STMT_ADD, number=ADD_RUNS)
        results.append(
            {
                "Scenario": scenario_name,
                "Benchmark": f"Add {TOTAL_LIMIT_ORDERS/1e6:.0f}M Orders",
                "Runs": ADD_RUNS,
                "Total Time (s)": time_add,
                "Avg. per Run (s)": time_add / ADD_RUNS,
            }
        )

        # --- Match Orders Benchmark ---
        print(f"  Running Match... ({MATCH_RUNS} runs of {MARKET_ORDER_COUNT} orders)")
        setup_match = get_setup_match(num_levels)
        time_match = timeit.timeit(
            setup=setup_match, stmt=STMT_MATCH, number=MATCH_RUNS
        )
        results.append(
            {
                "Scenario": scenario_name,
                "Benchmark": f"Match {MARKET_ORDER_COUNT/1e3:.0f}k Mkt Orders",
                "Runs": MATCH_RUNS,
                "Total Time (s)": time_match,
                "Avg. per Run (s)": time_match / MATCH_RUNS,
            }
        )

        # --- Cancel Orders Benchmark ---
        print(f"  Running Cancel... ({CANCEL_RUNS} runs of {CANCEL_BATCH_SIZE} orders)")
        setup_cancel = get_setup_cancel(num_levels)
        time_cancel = timeit.timeit(
            setup=setup_cancel, stmt=STMT_CANCEL, number=CANCEL_RUNS
        )
        results.append(
            {
                "Scenario": scenario_name,
                "Benchmark": f"Cancel {CANCEL_BATCH_SIZE/1e3:.0f}k Orders",
                "Runs": CANCEL_RUNS,
                "Total Time (s)": time_cancel,
                "Avg. per Run (s)": time_cancel / CANCEL_RUNS,
            }
        )

    # --- Print Results Table ---
    print("\n\n" + "=" * 70)
    print("Benchmark Results Summary")
    print("=" * 70)

    # Header
    print(
        f"{'Benchmark':<25} | {'Scenario':<25} | {'Runs':>5} | {'Total Time (s)':>15} | {'Avg. / Run (s)':>15}"
    )
    print("-" * 90)

    # Data
    for res in results:
        print(
            f"{res['Benchmark']:<25} | {res['Scenario']:<25} | {res['Runs']:>5} | {res['Total Time (s)']:>15.4f} | {res['Avg. per Run (s)']:>15.4f}"
        )

    # Loop over scenarios and types instead of repeating code
    for scenario in SCENARIOS.keys():  # e.g., "ShallowBook", "DeepBook"
        for profile_type in ["Additions", "Cancellations"]:

            print(f"\n--- cProfile Report: {scenario} {profile_type} ---")

            # Call the single, streamlined profiler function
            profile_operation(
                stream=sys.stdout,
                scenario=scenario,
                profile_type=profile_type,
                num_stats=5,  # Truncate to top 5 as requested
            )
            print("-" * 70)


if __name__ == "__main__":
    run_benchmarks()
