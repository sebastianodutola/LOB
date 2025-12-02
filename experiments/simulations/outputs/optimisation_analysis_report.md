# Optimal Skew Coefficient Analysis Report

## Power Law Model

Fitting: $\log(c^*) \sim a_0 + a_1 \cdot \log(informed\ frac) + a_2 \cdot \log(price\ vol)$

| Variable | Coefficient | Std Error | t-statistic | P>\|t\| |
|----------|-------------|-----------|-------------|-------|
| const | -9.3515 | 0.0530 | -176.480 | 0.0000 |
| informed fraction | -0.5655 | 0.0162 | -34.986 | 0.0000 |
| price volatility | 1.0007 | 0.0162 | 61.906 | 0.0000 |

**Model Diagnostics:**
- R-squared: 0.9403
- Adjusted R-squared: 0.9399
- F-statistic: 2528.16
- Prob (F-statistic): 3.4538e-197
- AIC: -173.93
- BIC: -162.59
- Number of observations: 324

## Power Law Model with Interaction Term

Fitting: $\log(c^*) \sim a_0 + a_1 \cdot \log(informed\ frac) + a_2 \cdot \log(price\ vol) + a_3 \cdot log(price\ vol) \cdot log(informed \ frac)$
| Variable | Coefficient | Std Error | t-statistic | P>\|t\| |
|----------|-------------|-----------|-------------|-------|
| const | -9.3225 | 0.0835 | -111.639 | 0.0000 |
| informed fraction | -0.5297 | 0.0812 | -6.522 | 0.0000 |
| price volatility | 1.0100 | 0.0263 | 38.418 | 0.0000 |
| lnIF * lnPV | 0.0115 | 0.0256 | 0.450 | 0.6531 |

**Model Diagnostics:**
- R-squared: 0.9403
- Adjusted R-squared: 0.9398
- F-statistic: 1681.32
- Prob (F-statistic): 1.7728e-195
- AIC: -172.13
- BIC: -157.01
- Number of observations: 324

## Summary Statistics

| Metric | Median | 10th Quantile | 25th Quantile | 75th Quantile | 90th Quantile | Min | Max |
|--------|------|-----|-----|-----|-----|-----|------|
| optimal sc-returns vs optimal sc-msd (log diff) | 1.137395e-01 | 0.000000e+00 | 2.729673e-02 | 2.742750e-01 |3.815000e-01 | 0.000000e+00 | 4.310632e+00
| optimal sc-returns vs optimal sc-pnl (log diff) | 0.000000e+00 | 0.000000e+00 | 0.000000e+00 | 0.000000e+00 |0.000000e+00 | 0.000000e+00 | 0.000000e+00
| optimality loss absolute returns | 0.000000e+00 | -8.578849e-08 | -7.631764e-09 | 1.060211e-07 |3.067041e-07 | -2.784257e-06 | 4.378977e-06
| optimality loss returns | 0.000000e+00 | -9.689516e-02 | -2.552320e-02 | 1.251754e-02 |7.669934e-02 | -3.972085e+00 | 6.483526e+00
| optimality loss msd | 0.000000e+00 | -5.353169e-02 | -1.279841e-02 | 3.645422e-02 |7.604807e-02 | -7.386804e-01 | 2.832303e+00
| optimality loss returns masked | 0.000000e+00 | -8.352782e-02 | -2.471074e-02 | 1.241801e-02 |5.666445e-02 | -4.489875e-01 | 5.128726e-01

## Fixed Informed Fraction (0.5)

|   price volatility |   optimal sc-returns |   average returns |        final pnl |
|-------------------:|---------------------:|------------------:|-----------------:|
|               0.02 |          3.18364e-06 |       4.7833e-06  |      1.00479e+06 |
|               0.04 |          4.51825e-06 |       2.81302e-06 |      1.00281e+06 |
|               0.06 |          8.85867e-06 |       7.41603e-07 |      1.00074e+06 |
|               0.08 |          1.09884e-05 |      -1.3648e-06  | 998638           |

## Fixed Price Volatility (0.05)

|   informed fraction |   optimal sc-returns |   average returns |        final pnl |
|--------------------:|---------------------:|------------------:|-----------------:|
|                 0.2 |          1.12884e-05 |       3.44029e-06 |      1.00344e+06 |
|                 0.4 |          8.1711e-06  |       2.45811e-06 |      1.00246e+06 |
|                 0.6 |          5.4556e-06  |       9.67213e-07 |      1.00097e+06 |
|                 0.8 |          4.76829e-06 |      -5.98263e-07 | 999402           |
