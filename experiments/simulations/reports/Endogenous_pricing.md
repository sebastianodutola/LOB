# Endogenous Pricing and Market Maker Profit Maximization

# Introduction

Market makers are often described as liquidity providers, but this characterization obscures their deeper function in price discovery. A fundamental question in market microstructure is: what mechanism compels market makers to set efficient prices?

Most academic models (e.g., Avellaneda–Stoikov) assume the mid-price evolves exogenously as an Ito process, treating it as an external environmental factor to which the market maker responds. While this framework is useful for deriving closed-form optimal strategies, it sidesteps the question of how prices come to reflect fundamental value in the first place. If market makers simply quote around an externally given mid-price, they are passive participants in price formation rather than active contributors to price discovery.
This report investigates price formation through an endogenous pricing framework where no stochastically evolving mid-price is directly observable to the market maker. Instead, the market maker must discover the asset's fundamental value through the only signal available: the inventory consequences of its trading decisions. The central hypothesis is that profit maximization naturally compels efficient pricing—that is, a market maker optimizing for long-run profitability will converge toward quoting prices that accurately reflect the asset's fundamental value.

## Model Setup
The simulation employs the minimal possible setup to observe endogenous price discovery:

**Informed Traders:** Have access to the asset's fundamental value, which evolves as a random walk with normally distributed increments. Order arrivals follow a Poisson process with uniformly distributed integer volumes. Each order is a market order that crosses the spread. Crucially, each order has probability p of trading in the direction of the fundamental value (informed flow) and probability 1-p of trading against it (noise flow).

**Monopolistic Market Maker:** Posts two-sided quotes at a fixed spread s with no direct observation of the fundamental value. The market maker's only information channel is the inventory built from trading with informed and uninformed order flow. To manage inventory risk, the market maker employs a linear skewing strategy:

$$
\begin{align*}
B_t &= \text{mid}_t - \frac{s}{2} - c \cdot I_t \cdot \text{mid}_t  \\
A_t &= \text{mid}_t + \frac{s}{2} - c \cdot I_t \cdot \text{mid}_t
\end{align*}
$$

Where $c$ is the skew coefficient and $I_t$ is the signed inventory position (so that $I_t \cdot \text{mid}_t$ is the signed dollar exposure).

The mechanism of price discovery is adverse selection: when the market maker overvalues an asset, informed traders sell at the inflated price, causing toxic inventory accumulation that would realize losses if prices corrected. The market maker's skewing response to this inventory buildup constitutes its pricing adjustment toward fundamental value.

## Illustrative Example
The following simulation demonstrates that the mechanism can produce endogenous pricing. With an appropriately calibrated skew coefficient, the market maker's mid-price tracks the fundamental asset value despite having no direct observation of it:

![image](./figures/fig2.png)

Notably, the market maker achieves positive mark-to-market returns, suggesting that its pricing strategy—derived purely from inventory management—successfully navigates the adverse selection imposed by informed traders. This raises two critical questions that we investigate in the subsequent analysis:

**Optimal Skewing:** How does the optimal skew coefficient depend on market conditions (volatility, informed trader fraction)?

**Efficiency and Profit:** Is efficient pricing indeed the profit-maximizing strategy, or is this an artifact of particular parameter choices?

The remainder of this report addresses these questions through systematic experimentation, demonstrating that profit-driven market making endogenously produces efficient price discovery.

## Optimal Skewing

An exploratory plot of trajectories indicates that the correct skew coefficient makes the market maker sensitive enough to inventory accumulation that it may follow the fundamental value of the asset well, and yet doesn't overreact to a weak signal. In economic terms, the market maker must be sufficiently willing to unwind a position if it looks like the fundamental value has deviated from the mid-price, but musn't overpay in order to unwind.

![image])(./figures/fig1.png)

We might expect, therefore, that:
1) High asset volatility implies a higher optimal skew coefficient; the market maker must be more sensitive to the signal to be able to follow the higher volatility asset trajectory.
2) Higher informed trader fraction implies a lower optimal skew coefficient; the pricing signal is stronger and so the market maker can be less sensitive and still follow the asset trajectory. 

### Methodology

I use monte-carlo simulation and a simple but effective grid search to optimise the skew coefficient in different market regimes. I find optimal skew coefficients and the value of two different metrics at the optimal skew at 324 different market regimes $(\sigma, \gamma)$, where $\sigma = \{0.005 + 0.005i\}_{i=1}^18$ represents the market volatility and $\gamma = \{0.05 + 0.05\}_{i=1}^18$ represents the fraction of informed traders. 

At each regime point I perform a grid search across a skew coefficient set $c = \{1e-6 + i \cdot 2.5e-7}_{i=1}^40 \cup \{1e-5 + i \cdot 2.5e-6}_{i=1}^40$. This grid search was arrived upon after intial investigations revealed the optimal skew coefficient scaled logarithmically with asset-volatility.

Note: In order to justify the market regime range we can do a back of the napkin calculation: with an initial price of 




| informed fraction | price volatility | optimal coefficient | average returns   | final pnl      |
|-----------------|----------------|------------------|-----------------|----------------|
| 0.5             | 0.02           | 2.750000e-06     | 4.812768e-06    | 1.004820e+06  |
| 0.5             | 0.04           | 4.750000e-06     | 2.846395e-06    | 1.002848e+06  |
| 0.5             | 0.06           | 7.250000e-06     | 7.936532e-07    | 1.000793e+06  |
| 0.5             | 0.08           | 9.000000e-06     | -1.533427e-06   | 9.984693e+05  |

| informed fraction | price volatility | optimal coefficient | average returns   | final pnl      |
|-----------------|----------------|------------------|-----------------|----------------|
| 0.2             | 0.05           | 1.250000e-05     | 3.643743e-06    | 1.003647e+06  |
| 0.4             | 0.05           | 8.250000e-06     | 2.599404e-06    | 1.002600e+06  |
| 0.6             | 0.05           | 4.750000e-06     | 1.093102e-06    | 1.001093e+06  |
| 0.8             | 0.05           | 4.750000e-06     | -4.185457e-07   | 9.995819e+05  |
