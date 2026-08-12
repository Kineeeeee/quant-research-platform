# Quant Research Platform - Notes

Working document that grows with the project. The goal is one pipeline:

```
Raw data -> clean data -> research (find alpha) -> strategy -> backtest
```

If a piece doesn't help answer "does this actually make money?", it doesn't belong.

## Data pipeline

Files: `src/data/loader.py`, `src/data/cleaner.py`

Downloads historical prices from Yahoo Finance and cleans them. Everything downstream depends on this, so if the data is wrong (missing values, bad prices) the rest is garbage.

Key points:
- OHLCV is the raw material. Close price is what most calcs use.
- Adjusted prices matter - splits/dividends distort raw prices.
- Missing days (holidays, halts) get forward-filled rather than left as NaN, which would break rolling calculations.

Design choice: using free `yfinance` instead of a paid provider. Less reliable and occasionally gappy, but fine for research.

```python
raw = yf.download('AAPL', start='2020-01-01', end='2024-12-31')
# cleaner sorts by date, ffill/bfill gaps, drops all-NaN rows
```

## Backtesting engine

Files: `src/backtest/engine.py`, `portfolio.py`, `order.py`, `strategies/base.py`

Simulates trading on historical data so I can test an idea before risking any money. Event-driven: process one day at a time, in order, so there's no lookahead bias.

Main loop (`engine.py`):
1. Fill pending orders from the previous day at today's price.
2. Ask the strategy what to do today via `strategy.next(...)`.
3. Record equity = cash + market value of positions.

Pieces:
- `Order` - a trading instruction (dataclass with type/direction/status).
- `Portfolio` - tracks cash and positions, applies commission (0.1%) and slippage (0.05%) on each fill.
- `Strategy` base class - `setup()` computes indicators once, `next()` runs each bar. Concrete strategies subclass this.

Simplifications for now: market orders only, fills at close, fixed slippage. Real markets have limit orders, partial fills, and impact that depends on size. Risk controls come later once there's an actual strategy to constrain.

## Research: does alpha actually exist?

Files: `notebooks/01_momentum_research.ipynb`, `notebooks/02_mean_reversion.ipynb`

Before building strategies I wanted to check whether the patterns I'd trade are even real. Most trading ideas sound good and don't survive a proper test.

Process for each hypothesis: define the signal, rank stocks cross-sectionally each day, go long the top 20% / short the bottom 20%, measure forward returns, then t-test the long-short spread.

Findings so far:
- NB01 Momentum (6M lookback, 1M hold): past winners do keep winning, but the edge is modest. On non-overlapping monthly spreads: Sharpe ~0.67, p=0.042 (just significant). Drawdown is ugly (-43%). Worth building a strategy on, but with a vol/crash filter and realistic expectations - not a free lunch.
- NB02 Mean reversion (1-4 week): on large-cap US names, losers keep losing - this is really more momentum than reversion. So no short-term MR strategy on this universe. Probably needs small-caps or intraday horizons.

Stats notes to keep straight (learned the hard way in NB01):
- p < 0.05 = statistically significant (< 5% chance it's random).
- Overlapping forward returns inflate significance badly - consecutive daily 21-day returns share 20 days of data, so ~2300 daily obs are really only ~113 independent ones. My first run gave t~7, p~0, Sharpe 2.3, which was nonsense. After subsampling to non-overlapping windows: t~1.5, Sharpe ~0.5. Always subsample (or Newey-West) before trusting a t-stat on overlapping returns.

## Research: volatility clustering (NB03)

File: `notebooks/03_volatility_clustering.ipynb`

Studied SPY 2005-2024. Question: are big moves followed by big moves?

Findings:
- Raw daily returns have near-zero autocorrelation (lag-1 ~ -0.10) - you can't predict direction. Expected, markets are roughly efficient on direction.
- But ABSOLUTE returns are strongly autocorrelated (lag-1 ~ 0.32, still ~0.24 at lag 20). So volatility clusters even though direction doesn't. This is the classic GARCH/ARCH effect.
- Fat tails: extreme moves happen way more often than a normal distribution predicts.
- EWMA(span=30) vol forecast correlates ~0.68 with next-month realised vol (R^2 ~ 0.46). So vol is genuinely forecastable, unlike returns.

Why this matters for the platform: since vol is predictable but direction isn't, position sizing should key off vol, not off return forecasts. This is the motivation for the vol-adjusted momentum strategy and the vol-based sizing in the risk manager later on.

## First strategy + performance metrics

Files: `src/strategies/momentum.py`, `src/analytics/metrics.py`

First actual strategy: `SMACrossover`. Classic - hold when the short SMA (50d) is above the long SMA (200d), flat otherwise. It's a trend follower, so it should ride the momentum the research found. Simple on purpose - I wanted something to sanity-check the engine before building anything fancy.

Note: it's position-based, not event-based - it checks whether short > long each bar rather than detecting the exact crossover day. Good enough for a first pass.

Metrics (`metrics.py`) - can't judge a strategy on total return alone, need risk-adjusted numbers:
- `sharpe_ratio` - return per unit of volatility, annualised (x sqrt(252)).
- `max_drawdown` - worst peak-to-trough drop. This is what actually hurts.
- `daily_win_rate` - fraction of up days.
- `total_return` - overall % gain.

Sharpe is the headline number but drawdown matters just as much - a 0.8 Sharpe with a 15% max drawdown beats a 1.0 Sharpe that goes through -50%.

## More strategies

Files: `src/strategies/rsi.py`, `macd.py`, `bollinger.py`

Added a few more classic strategies to have something to compare against SMA and to exercise different signal types:

- `RSIReversion` - buy when RSI < 30 (oversold), sell when RSI > 70 (overbought). Mean-reversion. Uses the `ta` library for the RSI calc.
- `MACDStrategy` - buy/sell on MACD/Signal crossovers, detected via the histogram flipping sign. This one is a proper event-based crossover (tracks the previous bar's histogram), unlike the SMA one.
- `BollingerMeanReversion` - buy at the lower band, sell at the upper band.
- `BollingerBreakout` - the opposite: buy when price breaks *above* the upper band, sell below the lower. Same bands, opposite thesis. Kept both because which one works depends entirely on whether the market is trending or ranging - a nice illustration that the indicator isn't the strategy.

None of these are meant to be great on their own - they're building blocks and sanity checks for the engine.

## Tests

Files: `tests/test_metrics.py`, `tests/test_strategies.py`, `tests/test_portfolio.py`

Once there were a few strategies and the portfolio doing real accounting, I wanted a safety net before adding more moving parts. `pytest tests/ -v`.

What's covered:
- Metrics: known-value checks (e.g. 100->120->90 gives -25% drawdown), plus edge cases - zero-std Sharpe returns NaN instead of dividing by zero, win rate excludes flat days, 100% drawdown.
- Strategies: SMA golden/death crosses fire correctly, no double-buy while already long, no signal while indicators are still NaN. Same for RSI oversold/overbought.
- Portfolio: buy/sell update cash and positions, commission + slippage are applied, and it correctly rejects buys with insufficient cash / sells with no position.

The edge cases are the point - the happy path rarely breaks, the divide-by-zero and off-by-one cases do.

## Risk management

Files: `src/backtest/risk_manager.py`, and the risk hook in `engine.py`

Up to now the engine filled any order the strategy produced. That's not how you'd actually trade - one oversized position or a bad streak can wipe you out. So the engine now runs every buy past a `RiskManager` before filling it; a rejected order is marked REJECTED and dropped.

Rules it enforces:
- Position cap: no single position over 20% of equity (concentration).
- Max 5 open positions at once.
- Drawdown circuit breaker: once equity is down >25% from its peak, stop opening new risk. Live to trade another day.
- 2% rule: assuming a 5% stop-loss, the implied loss on a trade can't exceed 2% of equity. This is the classic fixed-fractional sizing idea.

It also does sizing, not just vetoing:
- `calculate_position_size` - the 2%-rule size, capped by the 20% limit.
- `calculate_vol_adjusted_size` - scales that by vol_target / current_vol so high-vol names get smaller positions. This is the NB03 finding (vol is forecastable) turned into an actual sizing rule. Scalar capped to 0.25x-2x so a very calm stretch doesn't lever up absurdly.

Sells always pass - they only reduce exposure.

## Vol-adjusted momentum

Files: `src/strategies/vol_momentum.py`, `examples/tune_vol_momentum.py`

This is the first strategy that actually uses the research rather than being a textbook indicator. `VolAdjustedMomentum` combines three threads:
- Signal from the SMA crossover (NB01 momentum).
- Sizing from EWMA vol (NB03: vol is the forecastable part, so size off it - smaller positions when vol is high, capped 0.25x-2x).
- A long-term trend filter (price vs 200d SMA): only go long in an uptrend, force an exit when the market rolls over. Plain SMA momentum gets destroyed in bear markets, so this is the guard rail.
- A vol cutoff: sit out entirely when vol blows past 2x its median.

`tune_vol_momentum.py` is a small grid search over short/long windows, the vol filter multiplier, and base size. Nothing fancy - just eyeballing which parameter regions give a decent Sharpe without the drawdown getting silly. (Proper out-of-sample validation comes next with walk-forward - a single in-sample grid search is exactly how you fool yourself.)
