import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from src.portfolio.optimizer import PortfolioOptimizer


class EfficientFrontier:
    """
    Plots the risk/return cloud of random portfolios with the max-Sharpe and
    equal-weight points marked. The upper-left edge of the cloud is the
    efficient frontier - best return for each level of risk.
    """

    def __init__(self, returns: pd.DataFrame, n_portfolios: int = 5000):
        self.returns = returns
        self.n_portfolios = n_portfolios
        self.optimizer = PortfolioOptimizer(returns)

    def generate_random_portfolios(self) -> pd.DataFrame:
        # Monte Carlo random weights; the upper edge of the cloud is the frontier
        results = []
        n_assets = len(self.returns.columns)
        for _ in range(self.n_portfolios):
            weights = np.random.random(n_assets)
            weights = weights / weights.sum()
            stats = self.optimizer.portfolio_stats(weights)
            stats['weights'] = weights
            results.append(stats)
        return pd.DataFrame(results)

    def plot(self):
        df = self.generate_random_portfolios()

        w_max_sharpe = self.optimizer.mean_variance(target='max_sharpe')
        stats_max_sharpe = self.optimizer.portfolio_stats(w_max_sharpe)
        w_equal = self.optimizer.equal_weight()
        stats_equal = self.optimizer.portfolio_stats(w_equal)

        fig, ax = plt.subplots(figsize=(10, 7))
        scatter = ax.scatter(df['ann_vol'] * 100, df['ann_return'] * 100,
                             c=df['sharpe'], cmap='viridis', s=5, alpha=0.5)
        plt.colorbar(scatter, ax=ax, label='Sharpe Ratio')

        ax.scatter(stats_max_sharpe['ann_vol'] * 100, stats_max_sharpe['ann_return'] * 100,
                   marker='*', s=300, color='red', zorder=5,
                   label=f'Max Sharpe ({stats_max_sharpe["sharpe"]:.2f})')
        ax.scatter(stats_equal['ann_vol'] * 100, stats_equal['ann_return'] * 100,
                   marker='D', s=100, color='blue', zorder=5,
                   label=f'Equal Weight ({stats_equal["sharpe"]:.2f})')

        for asset in self.optimizer.assets:
            asset_ret = self.optimizer.mean_returns[asset] * 252 * 100
            asset_vol = self.returns[asset].std() * np.sqrt(252) * 100
            ax.scatter(asset_vol, asset_ret, marker='o', s=50, color='black', zorder=5)
            ax.annotate(asset, (asset_vol, asset_ret), fontsize=8, ha='left', va='bottom')

        ax.set_xlabel('Annual Volatility (%)')
        ax.set_ylabel('Annual Return (%)')
        ax.set_title('Efficient Frontier')
        ax.legend(loc='upper left')
        plt.tight_layout()
        plt.show()
