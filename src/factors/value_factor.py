import pandas as pd
import numpy as np
from src.factors.factor_base import Factor


class ValueFactor(Factor):
    """
    Price-based value proxy. With no fundamentals (no P/E, P/B), the best we
    can do is treat big past underperformers as "cheap" - so the score is just
    the negative past return. It's the mirror image of momentum: value goes
    long the losers, momentum goes long the winners.
    """

    def __init__(self, lookback: int = 252):
        super().__init__(name=f"Value_{lookback}d")
        self.lookback = lookback

    def compute(self, prices: pd.DataFrame) -> pd.DataFrame:
        return -prices.pct_change(self.lookback)
