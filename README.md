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

Built the first research-driven strategy: vol-adjusted momentum (SMA signal +
EWMA vol sizing + trend filter). Engine enforces risk limits and vol-based
sizing; classic strategies (SMA, RSI, MACD, Bollinger) all run through it,
scored with Sharpe / max drawdown / win rate and covered by unit tests. Next:
validate out-of-sample.
