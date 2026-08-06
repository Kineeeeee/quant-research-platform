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

Several classic strategies now run through the engine: SMA crossover, RSI
reversion, MACD, and Bollinger (both mean-reversion and breakout). Scored
with Sharpe / max drawdown / win rate. Next: proper testing and risk
controls.
