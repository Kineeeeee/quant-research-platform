import pandas as pd
import numpy as np


class FeatureBuilder:
    """
    Turn a price series into an ML feature matrix X and forward-return target y.
    Everything is built from past-only data so there's no lookahead in the
    features themselves - the only forward-looking column is the target.
    """

    def __init__(self, prices: pd.Series):
        self.prices = prices

    def build(self, forward_period: int = 21) -> tuple:
        df = pd.DataFrame(index=self.prices.index)

        # momentum at several horizons - let the model pick which matter
        df['mom_5d'] = self.prices.pct_change(5)
        df['mom_10d'] = self.prices.pct_change(10)
        df['mom_21d'] = self.prices.pct_change(21)
        df['mom_63d'] = self.prices.pct_change(63)
        df['mom_126d'] = self.prices.pct_change(126)
        df['mom_252d'] = self.prices.pct_change(252)

        df['vol_21d'] = self.prices.pct_change().rolling(21).std() * np.sqrt(252)
        df['vol_63d'] = self.prices.pct_change().rolling(63).std() * np.sqrt(252)
        df['vol_ratio'] = df['vol_21d'] / df['vol_63d']   # >1 = vol picking up

        df['dist_sma50'] = (self.prices - self.prices.rolling(50).mean()) / self.prices.rolling(50).mean()
        df['dist_sma200'] = (self.prices - self.prices.rolling(200).mean()) / self.prices.rolling(200).mean()

        delta = self.prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
        rs = gain / loss
        df['rsi_14'] = 100 - (100 / (1 + rs))

        y = self.prices.pct_change(forward_period).shift(-forward_period)

        X = df.dropna()
        y = y.loc[X.index].dropna()
        X = X.loc[y.index]
        return X, y
