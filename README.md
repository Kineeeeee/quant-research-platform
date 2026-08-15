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

Added walk-forward validation (in-sample optimise, out-of-sample test, with an
overfitting flag) so strategies get judged out-of-sample, not on the history
they were tuned on. Vol-adjusted momentum, risk limits, the classic strategies,
and unit tests are all in place.
