import pandas as pd
import numpy as np
from typing import Dict, Optional
from scipy import stats
from src.factors.factor_base import Factor


class FactorEngine:
    """Compute factor scores -> rank cross-sectionally -> long/short quintiles -> measure."""

    def __init__(
        self,
        prices: pd.DataFrame,
        factor: Factor,
        long_pct: float = 0.20,
        short_pct: float = 0.20,
    ):
        self.prices = prices
        self.factor = factor
        self.long_pct = long_pct
        self.short_pct = short_pct

        self.scores: Optional[pd.DataFrame] = None
        self.ranks: Optional[pd.DataFrame] = None
        self.long_returns: Optional[pd.Series] = None
        self.short_returns: Optional[pd.Series] = None
        self.spread_returns: Optional[pd.Series] = None
        self.metrics: Optional[Dict] = None

    def run(self, holding_period: int = 21) -> Dict:
        self.scores = self.factor.compute(self.prices)
        self.ranks = self.scores.rank(axis=1, pct=True)

        long_mask = self.ranks >= (1 - self.long_pct)
        short_mask = self.ranks <= self.short_pct

        fwd_returns = self.prices.pct_change(holding_period).shift(-holding_period)

        self.long_returns = fwd_returns[long_mask].mean(axis=1).dropna()
        self.short_returns = fwd_returns[short_mask].mean(axis=1).dropna()
        self.spread_returns = (self.long_returns - self.short_returns).dropna()

        self.metrics = self._compute_metrics(holding_period)
        return self.metrics

    def _compute_metrics(self, holding_period: int) -> Dict:
        # got burned by this in NB01: spread is daily but each point is a
        # holding_period-day forward return, so consecutive points share almost
        # all their data -> not independent. Feeding the raw daily series to a
        # t-test pretends ~1700 obs when there are really ~80, and the t-stat
        # blows up by ~sqrt(holding_period). Take every holding_period-th point
        # so the windows don't overlap. Crude vs Newey-West but easy to trust.
        indep = self.spread_returns.iloc[::holding_period].dropna()
        ann_sharpe = indep.mean() / indep.std() * np.sqrt(252 / holding_period)
        pct_positive = (indep > 0).mean() * 100
        t_stat, p_value = stats.ttest_1samp(indep, 0)

        return {
            'factor_name': self.factor.name,
            'mean_spread': indep.mean(),
            'ann_sharpe': ann_sharpe,
            't_stat': t_stat,
            'p_value': p_value,
            'pct_positive': pct_positive,
            'long_avg': self.long_returns.mean(),
            'short_avg': self.short_returns.mean(),
            'observations': len(indep),
            'holding_period': holding_period,
        }

    def compute_ic(self) -> pd.Series:
        """Information Coefficient: daily rank correlation of score vs forward return. IC > 0.05 is decent."""
        fwd_returns = self.prices.pct_change(21).shift(-21)
        ic_series = pd.Series(index=self.scores.index, dtype=float)
        # IC each day = how well today's ranking lines up with next-month returns.
        # Spearman not Pearson - we only care about the ordering (rank the stocks
        # right), not the exact magnitudes, and it shrugs off outliers.
        for date in self.scores.index:
            scores = self.scores.loc[date].dropna()
            fwd_ret = fwd_returns.loc[date].dropna()
            common_tickers = scores.index.intersection(fwd_ret.index)
            # need enough names to rank or the correlation is meaningless; skip
            # thin days rather than let a 2-stock day produce a spurious +/-1.
            if len(common_tickers) > 5:
                ic, _ = stats.spearmanr(scores[common_tickers], fwd_ret[common_tickers])
                ic_series[date] = ic
        return ic_series

    def print_summary(self):
        if self.metrics is None:
            print("No results to display. Run `run()` first.")
            return
        m = self.metrics
        print("\n=== FACTOR ANALYSIS SUMMARY ===")
        print(f"Factor: {m['factor_name']}")
        print(f"Holding Period: {m['holding_period']} days")
        print(f"Mean Spread: {m['mean_spread']*100:.2f}%")
        print(f"Annualised Sharpe: {m['ann_sharpe']:.2f}")
        print(f"t-stat: {m['t_stat']:.3f}, p-value: {m['p_value']:.4g}")
        print(f"% Positive: {m['pct_positive']:.1f}%")
        print(f"Long Avg: {m['long_avg']*100:.2f}%, Short Avg: {m['short_avg']*100:.2f}%")
        print(f"Observations: {m['observations']} (non-overlapping)")
        print("Conclusion:", "SIGNIFICANT" if m['p_value'] < 0.05 else "NOT SIGNIFICANT")
