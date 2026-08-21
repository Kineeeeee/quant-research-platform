# Equal weight vs mean-variance vs risk parity on sector ETFs, then plot the frontier.
import sys
sys.path.insert(0, '.')

import yfinance as yf
from src.portfolio.optimizer import PortfolioOptimizer
from src.portfolio.efficient_frontier import EfficientFrontier

TICKERS = ['XLK', 'XLF', 'XLE', 'XLV', 'XLY', 'XLP', 'XLI', 'XLU']

raw = yf.download(TICKERS, start='2018-01-01', end='2024-12-31', auto_adjust=True, progress=False)
prices = raw['Close'].dropna(axis=1, how='all').ffill()
returns = prices.pct_change().dropna()

print(f'Assets: {list(returns.columns)}')
print(f'Period: {returns.index[0].date()} to {returns.index[-1].date()}')
print()

opt = PortfolioOptimizer(returns)

opt.print_allocation(opt.equal_weight(), "Equal Weight")
print()
opt.print_allocation(opt.mean_variance(), "Max Sharpe (Markowitz)")
print()
opt.print_allocation(opt.risk_parity(), "Risk Parity")
print()

ef = EfficientFrontier(returns, n_portfolios=3000)
ef.plot()
