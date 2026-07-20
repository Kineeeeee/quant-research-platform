# Quant Research Platform

A personal project to learn quantitative research by building the whole
workflow from scratch in Python: pull market data, test whether patterns
actually predict returns, turn the ones that work into strategies, and
backtest them honestly.

Starting small and adding pieces as I learn them.

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

Early days. Just the project skeleton and data plumbing for now.
