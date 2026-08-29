import pandas as pd
from typing import Dict, List
from src.infrastructure.config import ExperimentConfig
from src.infrastructure.experiment import ExperimentTracker


class ExperimentRunner:
    """Config -> data -> strategy -> backtest -> metrics -> tracker, in one call."""

    def __init__(self):
        self.tracker = ExperimentTracker()

    def run_from_config(self, config_path: str) -> Dict:
        config = ExperimentConfig.from_file(config_path)

        # imports kept local: the runner sits above most of the package, so
        # importing at module top risks circular imports
        from src.data.loader import DataLoader
        from src.data.cleaner import DataCleaner

        data = DataLoader.fetch_historical_data(
            config.data['ticker'], config.data['start'], config.data['end']
        )
        DataLoader.save_raw_data(data, config.data['ticker'])
        clean = DataCleaner.clean_data(config.data['ticker'])

        from src.strategies.momentum import SMACrossover
        from src.strategies.rsi import RSIReversion
        from src.strategies.vol_momentum import VolAdjustedMomentum

        STRATEGY_MAP = {
            'SMACrossover': SMACrossover,
            'RSIReversion': RSIReversion,
            'VolAdjustedMomentum': VolAdjustedMomentum,
        }
        strategy = STRATEGY_MAP[config.strategy](**config.params)

        from src.backtest.engine import BacktestEngine
        from src.analytics import metrics

        engine = BacktestEngine(
            clean, strategy,
            initial_capital=config.backtest.get('initial_capital', 100000),
            ticker=config.data['ticker'],
        )
        equity = engine.run()

        returns = metrics.calculate_returns(equity)
        result_metrics = {
            'sharpe': metrics.sharpe_ratio(returns),
            'max_drawdown': metrics.max_drawdown(equity) * 100,
            'total_return': (equity['equity'].iloc[-1] / equity['equity'].iloc[0] - 1) * 100,
        }

        self.tracker.log(
            name=config.strategy,
            params=config.params,
            metrics=result_metrics,
            data_period=f"{config.data['start']} to {config.data['end']} {config.data['ticker']}",
            notes=config.notes,
        )
        return result_metrics

    def run_sweep(self, base_config: Dict, param_grid: Dict[str, List]) -> pd.DataFrame:
        import itertools
        from src.data.loader import DataLoader
        from src.data.cleaner import DataCleaner
        from src.strategies.momentum import SMACrossover
        from src.strategies.rsi import RSIReversion
        from src.strategies.vol_momentum import VolAdjustedMomentum
        from src.backtest.engine import BacktestEngine
        from src.analytics import metrics

        STRATEGY_MAP = {
            'SMACrossover': SMACrossover,
            'RSIReversion': RSIReversion,
            'VolAdjustedMomentum': VolAdjustedMomentum,
        }

        # download once, reuse across every combo - re-fetching per run is slow
        # and hammers the data source for no reason
        data = DataLoader.fetch_historical_data(
            base_config['data']['ticker'], base_config['data']['start'], base_config['data']['end']
        )
        DataLoader.save_raw_data(data, base_config['data']['ticker'])
        clean = DataCleaner.clean_data(base_config['data']['ticker'])

        keys = list(param_grid.keys())
        values = list(param_grid.values())
        combos = [dict(zip(keys, v)) for v in itertools.product(*values)]

        results = []
        for combo in combos:
            strategy = STRATEGY_MAP[base_config['strategy']](**combo)
            engine = BacktestEngine(
                clean, strategy,
                initial_capital=base_config.get('backtest', {}).get('initial_capital', 100000),
                ticker=base_config['data']['ticker'],
            )
            equity = engine.run()

            returns = metrics.calculate_returns(equity)
            result_metrics = {
                'sharpe': metrics.sharpe_ratio(returns),
                'max_drawdown': metrics.max_drawdown(equity) * 100,
                'total_return': (equity['equity'].iloc[-1] / equity['equity'].iloc[0] - 1) * 100,
            }

            self.tracker.log(
                name=base_config['strategy'],
                params=combo,
                metrics=result_metrics,
                data_period=f"{base_config['data']['start']} to {base_config['data']['end']} {base_config['data']['ticker']}",
            )
            results.append({**combo, **result_metrics})

        return pd.DataFrame(results)
