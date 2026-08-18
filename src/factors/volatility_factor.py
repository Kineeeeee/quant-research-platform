import pandas as pd
import numpy as np
from src.factors.factor_base import Factor


class VolatilityFactor(Factor):
    """
    Low-volatility anomaly: contrary to CAPM, calmer stocks tend to earn
    better risk-adjusted returns. Score = -rolling vol, so low vol ranks high
    and becomes a long candidate.
    """

    def __init__(self, window: int = 63):
        super().__init__(name=f"LowVol_{window}d")
        self.window = window

    def compute(self, prices: pd.DataFrame) -> pd.DataFrame:
        daily_returns = prices.pct_change().dropna()
        rolling_vol = daily_returns.rolling(self.window).std() * np.sqrt(252)
        return -rolling_vol
