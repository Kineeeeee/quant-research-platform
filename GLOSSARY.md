# Glossary

Terms I kept having to look up while building this, written back in my own
words so future-me doesn't have to re-google them. Roughly in the order they
show up in the project.

## Basic market concepts

**Stock** - a share of ownership in a company. Buy AAPL and you own a sliver of Apple. Price moves on supply and demand.

**Ticker** - the short code: AAPL, MSFT, NVDA, SPY (SPY = an ETF tracking the whole S&P 500).

**Long / Short** - long = buy expecting the price to rise. Short = sell borrowed shares expecting it to fall, buy back cheaper later.

**Position** - how many shares you hold. Long = you own them, short = you owe them, flat = nothing.

**Portfolio** - all your positions plus cash.

**Equity** - total value = cash + shares * current price. $20k cash + 50 AAPL at $180 = $29k.

## Price data

**OHLCV** - the five daily numbers: Open, High, Low, Close, Volume. Close is the one most calculations use; Volume is a rough liquidity gauge.

**Adjusted price** - price corrected for splits and dividends. Apple's 4-for-1 split in 2020 took the price from ~$500 to ~$125; unadjusted that looks like a 75% crash that never happened. `auto_adjust=True` in yfinance handles it.

**Return** - percentage change: `(price_today - price_yesterday) / price_yesterday`. In pandas, `prices.pct_change()`.

**Forward return** - the return looking *ahead*, i.e. the thing you're trying to predict. `shift(-21)` gives the 21-day forward return. Research only - you can't trade on data you don't have yet.

## Risk

**Volatility** - how much returns bounce around, measured as their standard deviation. Usually annualised by multiplying daily std by sqrt(252).

**Drawdown** - the drop from a peak. Max drawdown is the worst peak-to-trough fall, and it's what actually makes you quit a strategy, more than a low average return.

**Risk-free rate** - what you'd earn with zero risk (T-bills). The baseline Sharpe measures excess return over.

## Performance metrics

**Sharpe ratio** - return per unit of volatility, `(mean - rf) / std`, annualised. The headline risk-adjusted number. ~1 is good, ~2 is suspicious on retail data.

**Win rate** - fraction of periods that were positive. Can be misleading on its own: a strategy can win often and still lose money if the losses are big.

**Information Coefficient (IC)** - rank correlation between a prediction and the realised return. IC > ~0.05 is a usable signal. Gentler than demanding a high R^2, which is hopeless on noisy returns.

## Technical indicators

**Moving average (SMA)** - rolling mean of price. Smooths noise to show the trend.

**Golden / death cross** - short MA crossing above the long MA (golden, bullish) or below it (death, bearish).

**RSI** - momentum oscillator, 0-100. Below 30 = oversold, above 70 = overbought (by convention).

**MACD** - difference between two EMAs vs its own signal line; the histogram flipping sign is the crossover trigger.

**Bollinger Bands** - a moving average plus/minus a couple of standard deviations. Price at the bands is "stretched" - mean-reversion wants to fade it, breakout wants to follow it.

## Quant research concepts

**Alpha** - return that isn't explained by just being exposed to the market. The thing everyone's hunting; mostly it isn't there.

**Beta** - sensitivity to the market. Beta 1 moves with it, >1 amplifies, <1 dampens.

**Factor** - a characteristic that sorts stocks into winners and losers (momentum, value, low-vol). Rank on it, go long the top, short the bottom.

**Cross-sectional** - comparing stocks *against each other* on the same day, rather than one stock over time.

**Overfitting** - tuning a model so well to the past that it only describes the noise and fails on new data. The default outcome if you're not careful.

**Walk-forward validation** - optimise on an in-sample block, test on the next out-of-sample block the optimiser never saw. The honest way to know if an edge is real.

**t-test / p-value** - is this result distinguishable from luck? p < 0.05 means <5% chance of seeing it by chance. Careful with overlapping data, which fakes significance (learned that the hard way in NB01).

## Trading mechanics

**Slippage** - the gap between the price you wanted and the price you got. Modelled here as a small fixed fraction.

**Commission** - the broker's cut per trade. Small per trade, death by a thousand cuts for a high-churn strategy.

**Liquidity** - how easily you can trade without moving the price. High volume = liquid.

**Market vs limit order** - market = fill now at whatever price is there. Limit = fill only at my price or better, might not fill at all.

**Bid-ask spread** - gap between the best buy and best sell quote. What a market maker earns, and a cost you pay crossing it.

## Statistics

**Mean / standard deviation** - average, and typical distance from the average.

**Normal distribution** - the bell curve. Returns are roughly normal but with fatter tails: extreme moves happen far more often than it predicts.

**Correlation** - how two series move together, -1 to +1. Low correlation between assets is what makes diversification work.

**Cointegration** - two series that individually wander like random walks but whose *spread* is mean-reverting. The basis for pairs trading (KO/PEP).

## Machine learning

**Feature / target** - inputs (X) and the thing you're predicting (y). Here, past-based signals vs forward return.

**Training / prediction** - fit the model on past data, then predict on unseen data.

**Overfitting (ML flavour)** - model memorises the training set, bombs out of sample. Finance data is so noisy this is the normal failure mode.

**StandardScaler** - rescale features to mean 0, std 1. Fit it on the training set *only* or you leak test-set info backwards.

**TimeSeriesSplit** - cross-validation that always trains on the past and tests on the future. Never shuffle time series.

**Ridge / Lasso** - linear regression with a penalty on big coefficients (Ridge shrinks, Lasso can zero them out). Keeps the model from overfitting noisy features.

**Random forest** - an ensemble of decision trees. Captures nonlinearities but overfits happily if you let it.

## Market microstructure

**Order book** - all the resting limit orders, bids on one side and asks on the other, sorted by price.

**Market maker** - posts both a bid and an ask, earns the spread, and manages the inventory it accumulates.

**Mid price** - halfway between best bid and best ask. The usual "fair price" reference.

**Inventory risk** - the market maker's real problem: end up heavily long or short and a price move hurts. Managed by skewing quotes to lean against the position.

## Code shorthand I use a lot

- `DataFrame` / `Series` - pandas table / single column.
- `.pct_change(N)` - percentage change over N periods.
- `.rolling(N).mean()` - N-period moving average.
- `.shift(N)` - move data forward (N>0, past) or back (N<0, future). Negative shift is for building targets only.
- `.rank(axis=1, pct=True)` - rank across columns (cross-sectional), as a percentile.
- `np.sqrt(252)` - the factor to annualise a daily stat (252 trading days/year).
- `scipy.optimize.minimize` - the solver behind mean-variance (minimise -Sharpe).
- `heapq` - min-heap, used for the order book (store -price for the bid side to fake a max-heap).
