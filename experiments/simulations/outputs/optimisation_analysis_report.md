# Optimal Skew Coefficient Analysis Report

## Power Law Model

Fitting: log(optimal_sc) ~ const + β₁·log(informed_frac) + β₂·log(price_vol)

| Variable | Coefficient | Std Error | t-statistic | P>\|t\| |
|----------|-------------|-----------|-------------|-------|
| const | -9.2612 | 0.0452 | -204.766 | 0.0000 |
| informed fraction | -0.5837 | 0.0138 | -42.309 | 0.0000 |
| price volatility | 1.0278 | 0.0138 | 74.497 | 0.0000 |

**Model Diagnostics:**
- R-squared: 0.9581
- Adjusted R-squared: 0.9578
- F-statistic: 3669.94
- Prob (F-statistic): 7.3692e-222
- AIC: -276.55
- BIC: -265.20
- Number of observations: 324

## Summary Statistics

| Metric | Mean | Std | Min | Max |
|--------|------|-----|-----|-----|
| relative difference optimal sc-returns vs optimal sc-msd | 1.388757e-01 | 1.783728e-01 | -1.367386e+00 | 9.304807e-01 |
| relative difference optimal sc-returns vs optimal sc-pnl | 0.000000e+00 | 0.000000e+00 | 0.000000e+00 | 0.000000e+00 |

## Fixed Informed Fraction (0.5)

|   price volatility |   optimal sc-returns |   average returns |        final pnl |
|-------------------:|---------------------:|------------------:|-----------------:|
|               0.02 |          2.56659e-06 |       4.85518e-06 |      1.00486e+06 |
|               0.04 |          5.31063e-06 |       2.80603e-06 |      1.00281e+06 |
|               0.06 |          8.62328e-06 |       7.37347e-07 |      1.00074e+06 |
|               0.08 |          1.12884e-05 |      -1.16342e-06 | 998838           |

## Fixed Price Volatility (0.05)

|   informed fraction |   optimal sc-returns |   average returns |        final pnl |
|--------------------:|---------------------:|------------------:|-----------------:|
|                 0.2 |          1.09884e-05 |       3.67679e-06 |      1.00368e+06 |
|                 0.4 |          8.62328e-06 |       2.56539e-06 |      1.00257e+06 |
|                 0.6 |          6.24197e-06 |       9.9548e-07  |      1.001e+06   |
|                 0.8 |          5.31063e-06 |      -8.19639e-07 | 999181           |
