# Walk-forward analysis. Tuning parameters on the whole history overfits - the
# strategy memorises the past and dies in the future. So we slide a window:
# optimise on an in-sample (IS) block, then measure on the next out-of-sample
# (OOS) block the optimiser never saw. A strategy that holds up across every
# OOS window is the only kind worth trusting.
import pandas as pd
import numpy as np
from typing import List, Dict, Tuple, Type
from src.strategies.base import Strategy
from src.backtest.engine import BacktestEngine
from src.analytics import metrics


class WalkForwardAnalyzer:

    def __init__(
        self,
        data: pd.DataFrame,
        strategy_class: Type[Strategy],
        train_period_days: int = 504,   # ~2 trading years
        test_period_days: int = 252,    # ~1 trading year
        step_days: int = 252,
        initial_capital: float = 100000.0,
    ):
        self.data = data
        self.strategy_class = strategy_class
        self.train_period_days = train_period_days
        self.test_period_days = test_period_days
        self.step_days = step_days
        self.initial_capital = initial_capital

    def generate_windows(self) -> List[Tuple[pd.DataFrame, pd.DataFrame]]:
        total_days = len(self.data)
        windows = []
        start = 0
        while start < total_days:
            train_end = start + self.train_period_days
            test_end = train_end + self.test_period_days

            if test_end > total_days:
                break

            train_data = self.data.iloc[start:train_end]
            test_data = self.data.iloc[train_end:test_end]

            windows.append((train_data, test_data))
            start += self.step_days
        return windows

    def run(self, strategy_params: Dict) -> Dict:
        """Run fixed params across every OOS window - a rolling out-of-sample check."""
        windows = self.generate_windows()
        results = []
        for i, (train_data, test_data) in enumerate(windows):
            strategy = self.strategy_class(**strategy_params)
            engine = BacktestEngine(test_data, strategy, self.initial_capital)
            equity_curve = engine.run()

            returns = metrics.calculate_returns(equity_curve)
            sharpe = metrics.sharpe_ratio(returns)
            max_dd = metrics.max_drawdown(equity_curve)
            total_return = (equity_curve['equity'].iloc[-1] / equity_curve['equity'].iloc[0] - 1) * 100

            results.append({
                'window': i,
                'start': test_data.index[0].date(),
                'end': test_data.index[-1].date(),
                'sharpe': sharpe,
                'max_drawdown': max_dd * 100,
                'total_return': total_return,
            })

        df_results = pd.DataFrame(results)
        return {
            'results': df_results,
            'avg_sharpe': df_results['sharpe'].mean(),
            'worst_sharpe': df_results['sharpe'].min(),
            'consistency': (df_results['sharpe'] > 0).mean() * 100,
            'total_windows': len(df_results),
        }

    def run_with_optimization(self, param_grid: Dict[str, List]) -> Dict:
        """Optimise params on each IS window, score on the matching OOS window."""
        import itertools

        windows = self.generate_windows()
        results = []

        for i, (train_data, test_data) in enumerate(windows):
            keys = list(param_grid.keys())
            values = list(param_grid.values())
            combos = [dict(zip(keys, v)) for v in itertools.product(*values)]

            best_sharpe_is = -np.inf
            best_params = combos[0]

            for params in combos:
                if 'short_window' in params and 'long_window' in params:
                    if params['short_window'] >= params['long_window']:
                        continue

                strategy = self.strategy_class(**params)
                engine = BacktestEngine(train_data, strategy, self.initial_capital)
                eq = engine.run()
                ret = metrics.calculate_returns(eq)
                s = metrics.sharpe_ratio(ret)

                if s > best_sharpe_is:
                    best_sharpe_is = s
                    best_params = params

            strategy = self.strategy_class(**best_params)
            engine = BacktestEngine(test_data, strategy, self.initial_capital)
            eq_oos = engine.run()
            ret_oos = metrics.calculate_returns(eq_oos)
            sharpe_oos = metrics.sharpe_ratio(ret_oos)

            results.append({
                'window': i,
                'start': test_data.index[0].date(),
                'end': test_data.index[-1].date(),
                'best_params': best_params,
                'is_sharpe': best_sharpe_is,
                'oos_sharpe': sharpe_oos,
                'degradation': sharpe_oos / best_sharpe_is if best_sharpe_is > 0 else np.nan,
            })

        df_results = pd.DataFrame(results)
        avg_is = df_results['is_sharpe'].mean()
        avg_oos = df_results['oos_sharpe'].mean()

        return {
            'results': df_results,
            'avg_is_sharpe': avg_is,
            'avg_oos_sharpe': avg_oos,
            'avg_degradation': avg_oos / avg_is if avg_is > 0 else np.nan,
            'overfitting_risk': 'HIGH' if avg_oos < avg_is * 0.5 else 'LOW',
            'total_windows': len(df_results),
        }
