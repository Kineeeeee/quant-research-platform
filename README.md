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

First strategy (SMA crossover) runs end-to-end through the engine, and I can
score it with Sharpe / max drawdown / win rate. Research so far: weak
momentum, no short-term mean reversion on large-caps, clear volatility
clustering. More strategies next.
