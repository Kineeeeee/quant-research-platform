# Run the factor engine on 24 US stocks: momentum, value, low-vol.
import sys
sys.path.insert(0, '.')

import yfinance as yf
from src.factors.factor_engine import FactorEngine
from src.factors.momentum_factor import MomentumFactor
from src.factors.volatility_factor import VolatilityFactor
from src.factors.value_factor import ValueFactor

TICKERS = [
    'AAPL', 'MSFT', 'GOOGL', 'AMZN', 'META', 'NVDA', 'AMD',
    'JPM', 'BAC', 'GS', 'V', 'MA',
    'JNJ', 'PFE', 'UNH', 'MRK',
    'XOM', 'CVX',
    'WMT', 'COST', 'HD',
    'TSLA', 'NFLX', 'ADBE',
]

raw = yf.download(TICKERS, start='2015-01-01', end='2024-12-31', auto_adjust=True, progress=False)
prices = raw['Close'].dropna(axis=1, how='all').ffill()
print(f'Universe: {prices.shape[1]} stocks | {prices.shape[0]} days')
print()

factors = [
    MomentumFactor(lookback=126, skip=21),
    VolatilityFactor(window=63),
    ValueFactor(lookback=252),
]

for factor in factors:
    engine = FactorEngine(prices, factor)
    engine.run(holding_period=21)
    engine.print_summary()
    print()
