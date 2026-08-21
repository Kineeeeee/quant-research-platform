import pandas as pd
import numpy as np
from typing import Dict, Optional
from scipy.optimize import minimize


class PortfolioOptimizer:
    """
    Allocate capital across assets three ways: equal weight (1/N baseline),
    Markowitz mean-variance, and risk parity. Input is a returns DataFrame
    (rows=dates, cols=assets); every method returns weights summing to 1.
    """

    def __init__(self, returns: pd.DataFrame):
        self.returns = returns
        self.assets = list(returns.columns)
        self.n_assets = len(self.assets)
        self.mean_returns = returns.mean()
        self.cov_matrix = returns.cov()

    def equal_weight(self) -> np.ndarray:
        # 1/N baseline - surprisingly hard to beat OOS (noisy covariance)
        return np.array([1 / self.n_assets] * self.n_assets)

    def mean_variance(self, risk_free_rate: float = 0.0, target: str = 'max_sharpe') -> np.ndarray:
        if target == 'min_variance':
            def objective(weights):
                return np.sqrt(weights @ self.cov_matrix @ weights * 252)
        else:
            # minimise -Sharpe (scipy only minimises)
            def objective(weights):
                portfolio_return = np.sum(weights * self.mean_returns) * 252
                portfolio_vol = np.sqrt(weights @ self.cov_matrix @ weights * 252)
                return -(portfolio_return - risk_free_rate) / portfolio_vol

        # long-only, fully invested; seed from equal weight
        result = minimize(
            fun=objective,
            x0=np.array([1 / self.n_assets] * self.n_assets),
            method='SLSQP',
            bounds=[(0, 1)] * self.n_assets,
            constraints={'type': 'eq', 'fun': lambda w: np.sum(w) - 1},
        )
        return result.x

    def risk_parity(self) -> np.ndarray:
        # inverse-vol shortcut; only true risk parity when assets are uncorrelated
        vol = self.returns.std()
        inv_vol = 1 / vol
        return np.array(inv_vol / sum(inv_vol))

    def portfolio_stats(self, weights: np.ndarray) -> Dict:
        annual_return = np.sum(weights * self.mean_returns) * 252
        annual_vol = np.sqrt(weights @ self.cov_matrix @ weights * 252)
        return {'ann_return': annual_return, 'ann_vol': annual_vol, 'sharpe': annual_return / annual_vol}

    def print_allocation(self, weights: np.ndarray, method_name: str = "Portfolio"):
        sorted_data = sorted(zip(self.assets, weights), key=lambda x: x[1], reverse=True)
        print(f"\n{method_name} Allocation:")
        print("-" * 30)
        for asset, weight in sorted_data:
            print(f"{asset:12} {weight*100:6.2f}%")
        stats = self.portfolio_stats(weights)
        print("-" * 30)
        print(f"Annual Return: {stats['ann_return']:.2%}")
        print(f"Annual Vol:    {stats['ann_vol']:.2%}")
        print(f"Sharpe:        {stats['sharpe']:.3f}")
