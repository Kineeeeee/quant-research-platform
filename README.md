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

Added a market-microstructure layer: a limit order book (price-time priority
matching), an inventory-aware market maker, and a tick-by-tick simulator. This
rounds out the platform alongside research infrastructure, the ML pipeline,
stat arb, portfolio optimization, the factor engine, walk-forward validation,
and the strategy/backtest core.
