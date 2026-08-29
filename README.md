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

Added a research infrastructure layer: experiment configs, a JSON experiment
tracker, and a runner that goes config -> backtest -> logged results (with
parameter sweeps). Sits on top of the ML pipeline, stat arb, portfolio
optimization, the factor engine, walk-forward validation, and everything
before it.
