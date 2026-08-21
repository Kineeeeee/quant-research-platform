from src.strategies.momentum import SMACrossover
import pandas as pd
from src.backtest.engine import BacktestEngine
from src.analytics import metrics

class StrategyOptimizer:
    """Brute-force sweep of SMA parameter pairs, ranked by Sharpe. In-sample only - use walk-forward for real validation."""
    def __init__(self, data: pd.DataFrame, initial_capital: float = 100000.0):
        self.data = data
        self.initial_capital = initial_capital

    def optimize_sma(self, short_windows: list, long_windows: list):
        sharpe_list = []
        for short_win in short_windows:
            for long_win in long_windows:
                if short_win >= long_win:
                    continue
                
                sma_crossover = SMACrossover(short_win, long_win)
                engine = BacktestEngine(self.data, sma_crossover, self.initial_capital)
                equity_curve = engine.run()
                
                returns = metrics.calculate_returns(equity_curve)
                sharpe = metrics.sharpe_ratio(returns)
                
                sharpe_list.append({
                    'short': short_win, 
                    'long': long_win, 
                    'sharpe': sharpe
                })
                
        sharpe_list.sort(key=lambda x: x['sharpe'], reverse=True)
        return sharpe_list
