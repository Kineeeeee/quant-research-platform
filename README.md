# Quant Research Platform

A personal project to learn quantitative research by building the whole
workflow from scratch in Python: pull market data, test whether patterns
actually predict returns, turn the ones that hold up into strategies, and
backtest them honestly.

Built over a summer, one piece at a time. The guiding rule was that every part
has to help answer "does this actually make money?" - and a lot of the research
here concludes "no", which was the point.

## What's in it

- **Data** (`src/data`) - download and clean OHLCV from yfinance.
- **Research** (`notebooks/`) - momentum, mean-reversion, volatility clustering,
  sector rotation. Honest results: momentum is weak-but-real, vol clustering is
  strong, the rest is mostly noise. See `notebooks/research.ipynb` for the summary.
- **Strategies** (`src/strategies`) - SMA crossover, RSI, MACD, Bollinger, and a
  research-driven vol-adjusted momentum strategy.
- **Backtest engine** (`src/backtest`) - event-driven, with portfolio accounting
  (commission + slippage) and a risk manager (position caps, drawdown breaker,
  vol-based sizing).
- **Validation** (`src/analytics/walk_forward.py`) - walk-forward in-sample /
  out-of-sample testing with an overfitting flag.
- **Factor engine** (`src/factors`) - cross-sectional momentum / value / low-vol,
  scored by spread Sharpe and IC.
- **Portfolio** (`src/portfolio`) - equal weight, mean-variance, risk parity,
  efficient frontier.
- **Stat arb** (`src/stat_arb`) - cointegration scanner and pairs trading.
- **ML** (`src/ml`) - feature engineering + ridge/lasso/random forest with
  time-series CV. (Finding: barely beats plain momentum on a single stock.)
- **Infrastructure** (`src/infrastructure`) - experiment config, tracking, runner.
- **Microstructure** (`src/execution`) - a limit order book, an inventory-aware
  market maker, and a tick-by-tick simulator.

## Layout

```
src/
  data/            # download + clean price data
  strategies/      # trading rules
  backtest/        # engine, portfolio, orders, risk
  analytics/       # metrics, walk-forward, reporting, viz
  factors/         # cross-sectional factor research
  portfolio/       # multi-asset allocation
  stat_arb/        # cointegration + pairs
  ml/              # feature engineering + models
  infrastructure/  # experiment config / tracking / runner
  execution/       # order book + market making
notebooks/         # the research
examples/          # runnable end-to-end scripts
tests/             # unit tests
```

## Setup

```bash
pip install -r requirements.txt
```

Then try one of the example scripts:

```bash
python examples/run_backtest.py
python examples/run_walk_forward.py
python examples/run_pairs_trading.py
python examples/run_lob_simulation.py
```

## Notes

New here? `GLOSSARY.md` explains the terms; `DOCUMENTATION.md` is my running
build log with the reasoning behind each piece.

Tests: `pytest tests/`.
