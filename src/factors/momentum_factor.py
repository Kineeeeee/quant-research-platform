import pandas as pd
import numpy as np
from src.factors.factor_base import Factor


class MomentumFactor(Factor):
    """
    Classic Jegadeesh-Titman momentum: past return as the ranking signal,
    skipping the most recent month to avoid short-term reversal.
    """

    def __init__(self, lookback: int = 252, skip: int = 21):
        super().__init__(name=f"Momentum_{lookback}d_skip{skip}d")
        self.lookback = lookback
        self.skip = skip

    def compute(self, prices: pd.DataFrame) -> pd.DataFrame:
        prices_shifted = prices.shift(self.skip)
        return prices_shifted.pct_change(self.lookback - self.skip)
