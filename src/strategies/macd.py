"""
MACD (Moving Average Convergence Divergence) Strategy.

MACD is a popular momentum indicator combining trend-following and momentum:
- MACD Line = EMA(12) - EMA(26)
- Signal Line = EMA(9) of MACD Line
- Histogram = MACD Line - Signal Line

Signals:
- Buy when MACD crosses above Signal Line (histogram turns positive)
- Sell when MACD crosses below Signal Line (histogram turns negative)
"""
import pandas as pd
from src.strategies.base import Strategy


class MACDStrategy(Strategy):
    """
    Trading strategy based on MACD histogram crossover signals.
    """

    def __init__(
        self,
        fast_period: int = 12,
        slow_period: int = 26,
        signal_period: int = 9,
        trade_qty: float = 10,
    ):
        super().__init__()
        self.fast_period = fast_period
        self.slow_period = slow_period
        self.signal_period = signal_period
        self.trade_qty = trade_qty

        self.position_open = False
        self.prev_histogram = None  # Previous day's histogram for crossover detection

    def setup(self):
        """
        Compute MACD, Signal Line, and Histogram on the full dataset.
        """
        # Compute fast and slow EMAs
        ema_fast = self.data['Close'].ewm(span=self.fast_period, adjust=False).mean()
        ema_slow = self.data['Close'].ewm(span=self.slow_period, adjust=False).mean()

        # MACD Line = fast EMA - slow EMA
        self.data['MACD'] = ema_fast - ema_slow

        # Signal Line = EMA of MACD Line
        self.data['Signal'] = self.data['MACD'].ewm(span=self.signal_period, adjust=False).mean()

        # Histogram = MACD - Signal
        self.data['MACD_Hist'] = self.data['MACD'] - self.data['Signal']

    def next(self, timestamp: pd.Timestamp, row: pd.Series):
        """
        Trading logic: detect MACD/Signal crossover via histogram sign change.
        """
        histogram = row.get('MACD_Hist')

        if pd.isna(histogram):
            return

        # Bullish crossover: histogram flips from negative to non-negative
        if self.prev_histogram is not None and self.prev_histogram < 0 and histogram >= 0 and not self.position_open:
            self.buy(quantity=self.trade_qty)
            self.position_open = True

        # Bearish crossover: histogram flips from positive to non-positive
        if self.prev_histogram is not None and self.prev_histogram > 0 and histogram <= 0 and self.position_open:
            self.sell(quantity=self.trade_qty)
            self.position_open = False

        self.prev_histogram = histogram
