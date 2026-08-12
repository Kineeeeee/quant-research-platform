"""Quick grid search to find better params for VolAdjustedMomentum."""
import sys
sys.path.insert(0, '.')

from src.data.loader import DataLoader
from src.data.cleaner import DataCleaner
from src.strategies.vol_momentum import VolAdjustedMomentum
from src.backtest.engine import BacktestEngine
from src.analytics import metrics

data = DataLoader.fetch_historical_data('AAPL', '2020-01-01', '2023-12-31')
DataLoader.save_raw_data(data, 'AAPL')
clean = DataCleaner.clean_data('AAPL')

combos = [
    {'short_window': 50, 'long_window': 200, 'vol_filter_mult': 2.0, 'base_qty': 10},  # original
    {'short_window': 20, 'long_window': 50,  'vol_filter_mult': 3.0, 'base_qty': 20},
    {'short_window': 20, 'long_window': 100, 'vol_filter_mult': 3.0, 'base_qty': 20},
    {'short_window': 30, 'long_window': 100, 'vol_filter_mult': 2.5, 'base_qty': 15},
    {'short_window': 50, 'long_window': 200, 'vol_filter_mult': 3.0, 'base_qty': 20},
    {'short_window': 10, 'long_window': 50,  'vol_filter_mult': 2.5, 'base_qty': 25},
    {'short_window': 20, 'long_window': 50,  'vol_filter_mult': 5.0, 'base_qty': 20},
    {'short_window': 10, 'long_window': 30,  'vol_filter_mult': 5.0, 'base_qty': 30},
]

header = f"{'Short':>5} {'Long':>5} {'Filter':>6} {'Qty':>4} | {'Return%':>8} {'Sharpe':>7} {'DD%':>7} {'Trades':>6}"
print(header)
print('-' * len(header))

for c in combos:
    strategy = VolAdjustedMomentum(**c)
    engine = BacktestEngine(clean, strategy, 100000, ticker='AAPL')
    equity = engine.run()
    returns = metrics.calculate_returns(equity)
    sharpe = metrics.sharpe_ratio(returns)
    dd = metrics.max_drawdown(equity)
    total_ret = (equity['equity'].iloc[-1] / equity['equity'].iloc[0] - 1) * 100
    trades = len(engine.portfolio.trade_history)
    print(f"{c['short_window']:>5} {c['long_window']:>5} {c['vol_filter_mult']:>6.1f} {c['base_qty']:>4} | {total_ret:>+8.2f} {sharpe:>7.2f} {dd*100:>7.2f} {trades:>6}")
