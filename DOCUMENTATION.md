# Quant Research Platform - Notes

Working document that grows with the project. The goal is one pipeline:

```
Raw data -> clean data -> research (find alpha) -> strategy -> backtest
```

If a piece doesn't help answer "does this actually make money?", it doesn't
belong.

## Data pipeline

Files: `src/data/loader.py`, `src/data/cleaner.py`

Downloads historical prices from Yahoo Finance and cleans them. Everything
downstream depends on this, so if the data is wrong (missing values, bad
prices) the rest is garbage.

Key points:
- OHLCV is the raw material. Close price is what most calcs use.
- Adjusted prices matter - splits/dividends distort raw prices.
- Missing days (holidays, halts) get forward-filled rather than left as NaN,
  which would break rolling calculations.

Design choice: using free `yfinance` instead of a paid provider. Less
reliable and occasionally gappy, but fine for research.

```python
raw = yf.download('AAPL', start='2020-01-01', end='2024-12-31')
# cleaner sorts by date, ffill/bfill gaps, drops all-NaN rows
```


## Backtesting engine

Files: `src/backtest/engine.py`, `portfolio.py`, `order.py`, `strategies/base.py`

Simulates trading on historical data so I can test an idea before risking any
money. Event-driven: process one day at a time, in order, so there's no
lookahead bias.

Main loop (`engine.py`):
1. Fill pending orders from the previous day at today's price.
2. Ask the strategy what to do today via `strategy.next(...)`.
3. Record equity = cash + market value of positions.

Pieces:
- `Order` - a trading instruction (dataclass with type/direction/status).
- `Portfolio` - tracks cash and positions, applies commission (0.1%) and
  slippage (0.05%) on each fill.
- `Strategy` base class - `setup()` computes indicators once, `next()` runs
  each bar. Concrete strategies subclass this.

Simplifications for now: market orders only, fills at close, fixed slippage.
Real markets have limit orders, partial fills, and impact that depends on size.
Risk controls come later once there's an actual strategy to constrain.
