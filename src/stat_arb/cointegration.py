import pandas as pd
import numpy as np
from typing import List, Dict, Tuple
from itertools import combinations
from statsmodels.tsa.stattools import adfuller, coint


class CointegrationScanner:
    """
    Find pairs whose price spread is mean-reverting (cointegrated) even though
    each leg is a random walk on its own. Classic example: KO and PEP - both
    sell soda, so if KO jumps and PEP doesn't, the gap tends to close. Uses the
    Engle-Granger test (regress one on the other, ADF-test the residual).
    """

    def __init__(self, prices: pd.DataFrame):
        self.prices = prices
        self.tickers = list(prices.columns)

    def test_pair(self, ticker_a: str, ticker_b: str) -> Dict:
        t_stat, p_value, critical_values = coint(self.prices[ticker_a], self.prices[ticker_b])
        return {'ticker_a': ticker_a, 'ticker_b': ticker_b, 't_stat': t_stat,
                'p_value': p_value, 'is_cointegrated': p_value < 0.05}

    def find_pairs(self, p_threshold: float = 0.05) -> pd.DataFrame:
        # brute-force every pair. n^2, fine for a small universe. note: no
        # multiple-testing correction, so a few "pairs" here are pure luck -
        # eyeball the spread and half-life before trusting one.
        results = []
        for a, b in combinations(self.tickers, 2):
            data = self.test_pair(a, b)
            if data['is_cointegrated']:
                results.append(data)
        return pd.DataFrame(results).sort_values('p_value').reset_index(drop=True)

    def compute_spread(self, ticker_a: str, ticker_b: str) -> pd.DataFrame:
        price_a = self.prices[ticker_a]
        price_b = self.prices[ticker_b]

        # hedge ratio = OLS slope of A on B: how many B per A to be market-neutral
        beta = np.polyfit(price_b, price_a, 1)[0]
        spread = price_a - beta * price_b

        # 21-day rolling z-score, not full-sample: beta/mean drift over time
        z_score = (spread - spread.rolling(window=21).mean()) / spread.rolling(window=21).std()
        return pd.DataFrame({'price_a': price_a, 'price_b': price_b,
                             'spread': spread, 'z_score': z_score, 'beta': beta})

    def compute_half_life(self, spread: pd.Series) -> float:
        """Days for the spread to revert halfway. ~5-20d is tradeable, >60d too slow."""
        # Ornstein-Uhlenbeck: regress d(spread) on lagged spread, slope = theta.
        # theta<0 means mean-reverting; half-life = -ln(2)/theta.
        lag = spread.shift(1).dropna()
        delta = spread.diff(1).dropna()
        aligned_indices = delta.index.intersection(lag.index)
        theta = np.polyfit(lag.loc[aligned_indices], delta.loc[aligned_indices], 1)[0]
        return -np.log(2) / theta
