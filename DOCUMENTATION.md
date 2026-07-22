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
