# LOB — Level-3 Limit Order Book + Endogenous-Pricing Simulation Framework

## Overview

LOB implements a full Level-3 (per-order) limit-order book along with a simulation framework for studying price formation under endogenous pricing. The repository includes:
- A matching engine with add, cancel, and execution functionality at per-order granularity.
- Benchmark workloads evaluating scalability, cancellation cost, and micro-architectural effects.
- A market-making simulation environment supporting Monte-Carlo experiments across volatility and informed-trader regimes.
- A statistical analysis of a 324-point parameter grid, examining optimal skew behaviour and its dependence on volatility and informed-order flow.

The repository functions as a microstructure sandbox for experiments ranging from exchange-style matching to endogenous price formation in multi-agent settings.

### Why It Matters
- The engine reproduces core exchange mechanics, including price–time priority and realistic order-event handling. Benchmarks highlight practical performance considerations such as cancellation complexity and cache behaviour.
- The simulation layer enables controlled studies of how quoting strategies vary across regimes, providing a basis for experimentation with market-making and informed-trader interactions.
- Parameters, search procedures, and regression methods are documented to support reproducibility. The modular structure allows straightforward extension to alternative agent models or price-formation mechanisms.

### What’s Inside

| Component |	Purpose | 
| ----| ---|
|lob_sim/ | 	Core matching-engine implementation (add, cancel, execution, per-order book maintenance)|
|experiments/|	Scripts for running benchmark workloads and the Monte-Carlo market-maker simulations|
|Benchmark Report|	Performance analysis: matching speed, cancellation cost scaling, cache & memory effects|
|Simulation Report|	Results of endogenous-pricing experiments: optimal skew surfaces, regression fits, efficiency vs profit trade-offs|
|requirements.txt, setup.py|	Dependencies listing and installable package setup for ease of reuse|

## Getting Started

### Installation

The core limit‑order book engine can be installed from the repository root:

```bash
pip install .
```

This installs the `lob` package, which provides the order‑book engine, agent models, and simulation utilities.

### Basic Usage

The public API exposes the main components needed for constructing order‑flow environments:

```python
from lob import OrderBook, Order, MarketOrder, simulate_path

# Processing a single order
book = OrderBook()
book.process_order(Order(trader_id=101, price=100, volume=5, is_bid=True, is_market=False))

# Run a basic market_maker trajectory and produce summary statistics
price_vol = 0.01
informed_frac = 0.1
skew_coefficient = 1e-5
timesteps = 1_000

summary_stats = simulate_path(
    price_vol,
    informed_frac,
    skew_coefficient,
    timesteps=timesteps
)
```

This example illustrates minimal usage; most simulations will rely on higher‑level experiment scripts.

### Reproducing Figures and Reports

Figures and analysis outputs may be regenerated using:

```bash
python -m experiments.run_render
```

This generates trajectory plots, optimisation figures, and the optimisation‑analysis report in:

```
experiments/simulations/outputs/
```

### Running Benchmarks

Benchmark workloads can be executed via:

```bash
python -m experiments.run_benchmarks
```

These reproduce the add/cancel, matching, and cache‑sensitivity benchmarks described in the performance report.

### Simulation Experiments

The main simulation scripts are located in:

```
experiments/simulations/src/
```

These include:

- `path_visuals.py`  
- `optimal_coefficient_experiment.py`  
- `optimal_efficiency_experiment.py`

The optimal‑coefficient experiment must be run before the efficiency comparison, as the latter depends on its outputs.

These experiments are computationally expensive and are provided for completeness rather than routine execution.

Key Findings (Summary)
- Book matching throughput remains high (millions of order ops) under realistic load, but cancellations degrade as price-level depth increases due to an architecture trade-off (using a python library deque)
- In simulated markets with endogenous price formation, optimal skew (inventory-based quote adjustment) follows a consistent power-law scaling with volatility and fraction of informed traders across regimes.
- The “profit-optimal” and “efficiency-optimal” skews remain very close in the majority (~ 50%) of regimes, suggesting market maker profit incentives and market efficiency are well algined. 

These results hint at regime-dependent quoting strategies and illustrate well the service market makers provide: immediacy and price-discovery. 

Limitations & Next Steps
- The matching engine is written in Python: latency and memory–layout overheads remain far from production-grade C++/Rust implementations.
- The simulation uses stylised flows (Poisson arrivals, simple inventory-skew quoting) and omits features such as limit-order cancellation by age, latency effects and adaptive agents. Future work could consider multiple adaptive market makers and the competetive effect on spread.
- Statistical analysis currently reports point estimates without error bands or hypothesis testing; future work could add bootstrap-based confidence intervals or implement hypothesis testing.

Nonetheless, the repo constitutes a solid foundation — engine + experiment pipeline + economic analyis — that can be extended or reimplemented as needed.

## What I learned 

What I Learned
1. The central role of market makers in price discovery and liquidity provision. The spread is fundamentally the cost of immediacy and price certainty.
2.	The importance of inventory management as protection against adverse selection and as a determinant of profitable quoting behaviour.
3.	How to design robust, modular simulation infrastructure in Python, with clean separation of concerns, parallel execution, and reproducible Monte Carlo experiments.
4. How to use GitHub correctly, factor Python packages cleanly, and move data between components in a robust, reproducible way.

Licence

This project is released under the MIT License.
