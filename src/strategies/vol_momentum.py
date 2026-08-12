import pandas as pd
import numpy as np
from src.strategies.base import Strategy


class VolAdjustedMomentum(Strategy):
    """
    SMA crossover, but sized by volatility and gated by a long-term trend filter.

    Puts the research together: SMA crossover for the signal (NB01), EWMA vol
    for sizing since vol is the forecastable part (NB03), plus a trend filter
    and a vol cutoff so it sits out extreme regimes.
    """

    def __init__(
        self,
        short_window: int = 50,
        long_window: int = 200,
        trend_window: int = 200,
        vol_window: int = 30,
        vol_target: float = 0.10,
        vol_filter_mult: float = 2.0,
        base_qty: float = 10,
    ):
        super().__init__()
        self.short_window = short_window
        self.long_window = long_window
        self.trend_window = trend_window
        self.vol_window = vol_window
        self.vol_target = vol_target
        self.vol_filter_mult = vol_filter_mult
        self.base_qty = base_qty
        self.position_open = False

    def setup(self):
        self.data['SMA_Short'] = self.data['Close'].rolling(window=self.short_window).mean()
        self.data['SMA_Long'] = self.data['Close'].rolling(window=self.long_window).mean()
        self.data['SMA_Trend'] = self.data['Close'].rolling(window=self.trend_window).mean()

        daily_returns = self.data['Close'].pct_change()
        self.data['EWMA_Vol'] = daily_returns.ewm(span=self.vol_window).std() * np.sqrt(252)
        self.vol_median = self.data['EWMA_Vol'].median()

    def next(self, timestamp: pd.Timestamp, row: pd.Series):
        if pd.isna(row.get('SMA_Short')) or pd.isna(row.get('SMA_Long')):
            return
        if pd.isna(row.get('SMA_Trend')) or pd.isna(row.get('EWMA_Vol')):
            return

        current_price = row['Close']
        current_vol = row['EWMA_Vol']
        in_uptrend = current_price > row['SMA_Trend']

        # trend filter: bail out of longs when the market rolls over, don't buy into downtrends
        if not in_uptrend and self.position_open:
            self.sell(quantity=max(1, int(self.base_qty * 0.5)))
            self.position_open = False
            return
        if not in_uptrend:
            return

        # sit out extreme-vol regimes entirely
        if current_vol > self.vol_median * self.vol_filter_mult:
            return

        vol_scalar = self.vol_target / current_vol if current_vol > 0 else 1.0
        vol_scalar = np.clip(vol_scalar, 0.25, 2.0)
        qty = max(1, int(self.base_qty * vol_scalar))

        if row['SMA_Short'] > row['SMA_Long'] and not self.position_open:
            self.buy(quantity=qty)
            self.position_open = True
        elif row['SMA_Short'] < row['SMA_Long'] and self.position_open:
            self.sell(quantity=qty)
            self.position_open = False
