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

Engine now enforces risk limits (position caps, max open positions, drawdown
circuit breaker, 2% rule) and does vol-adjusted position sizing. Several
strategies run through it (SMA, RSI, MACD, Bollinger), scored with Sharpe /
max drawdown / win rate, all covered by unit tests.
