# Quant Research Platform

A personal project to learn quantitative research by building the whole
workflow from scratch in Python: pull market data, test whether patterns
actually predict returns, turn the ones that work into strategies, then backtest them


## Planned structure

```
src/
  data/         # download + clean price data
  strategies/   # trading rules
  backtest/     # simulate trading on historical data
  analytics/    # performance metrics
  utils/        # config, paths
```

## Setup

```bash
pip install -r requirements.txt
```

## Status

Added statistical arbitrage: a cointegration scanner (Engle-Granger, hedge
ratio, half-life) and a z-score pairs-trading strategy. On top of portfolio
optimization, the factor engine, walk-forward validation, vol-adjusted
momentum, risk limits, classic strategies, and unit tests.
