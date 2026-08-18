import pandas as pd
import numpy as np
from abc import ABC, abstractmethod


class Factor(ABC):
    """
    A factor scores every stock in the universe each day. Rank the scores
    cross-sectionally, go long the top quintile and short the bottom, then
    measure the forward returns. Higher score = stronger long candidate.
    """

    def __init__(self, name: str):
        self.name = name

    @abstractmethod
    def compute(self, prices: pd.DataFrame) -> pd.DataFrame:
        """Score each stock at each date. prices: index=dates, cols=tickers. Returns same shape."""
        pass

    def __repr__(self):
        return f"Factor({self.name})"
