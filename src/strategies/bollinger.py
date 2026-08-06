"""
Bollinger Bands Strategy.

Bollinger Bands = SMA(20) +/- 2 * Standard Deviation(20)
- Upper Band = SMA + 2*STD (dynamic resistance)
- Lower Band = SMA - 2*STD (dynamic support)
- Middle Band = SMA (moving average)

Mean Reversion approach:
- Buy when price touches/crosses Lower Band (price is cheap, expect reversion to SMA)
- Sell when price touches/crosses Upper Band (price is expensive, expect drop to SMA)

Breakout approach:
- Buy when price breaks above Upper Band (confirms strong uptrend)
- Sell when price breaks below Lower Band (confirms strong downtrend)
"""
import pandas as pd
from src.strategies.base import Strategy


class BollingerMeanReversion(Strategy):
    """
    Mean Reversion strategy using Bollinger Bands.
    Buy at Lower Band, sell at Upper Band.
    """

    def __init__(
        self,
        window: int = 20,
        num_std: float = 2.0,
        trade_qty: float = 10,
    ):
        super().__init__()
        self.window = window
        self.num_std = num_std
        self.trade_qty = trade_qty

        self.position_open = False

    def setup(self):
        """
        Compute Bollinger Bands: Middle, Upper, Lower.
        """
        # Middle Band (SMA)
        self.data['BB_Middle'] = self.data['Close'].rolling(window=self.window).mean()

        # Standard Deviation
        self.data['BB_Std'] = self.data['Close'].rolling(window=self.window).std()

        # Upper and Lower Bands
        self.data['BB_Upper'] = self.data['BB_Middle'] + (self.num_std * self.data['BB_Std'])
        self.data['BB_Lower'] = self.data['BB_Middle'] - (self.num_std * self.data['BB_Std'])

        # %B indicator: where price sits within the bands (0 = Lower, 1 = Upper)
        self.data['BB_PctB'] = (self.data['Close'] - self.data['BB_Lower']) / (self.data['BB_Upper'] - self.data['BB_Lower'])

    def next(self, timestamp: pd.Timestamp, row: pd.Series):
        """
        Mean Reversion logic: Buy at Lower Band, Sell at Upper Band.
        """
        if pd.isna(row.get('BB_Upper')) or pd.isna(row.get('BB_Lower')):
            return

        close = row['Close']

        # Buy signal: price at or below lower band
        if close <= row['BB_Lower'] and not self.position_open:
            self.buy(quantity=self.trade_qty)
            self.position_open = True

        # Sell signal: price at or above upper band
        if close >= row['BB_Upper'] and self.position_open:
            self.sell(quantity=self.trade_qty)
            self.position_open = False


class BollingerBreakout(Strategy):
    """
    Breakout strategy using Bollinger Bands.
    Buy when price breaks above Upper Band, sell when price breaks below Lower Band.
    (Opposite of Mean Reversion - suited for strongly trending markets)
    """

    def __init__(self, window: int = 20, num_std: float = 2.0, trade_qty: float = 10):
        super().__init__()
        self.window = window
        self.num_std = num_std
        self.trade_qty = trade_qty
        self.position_open = False

    def setup(self):
        """Compute Bollinger Bands (same as BollingerMeanReversion)."""
        self.data['BB_Middle'] = self.data['Close'].rolling(window=self.window).mean()
        self.data['BB_Std'] = self.data['Close'].rolling(window=self.window).std()
        self.data['BB_Upper'] = self.data['BB_Middle'] + (self.num_std * self.data['BB_Std'])
        self.data['BB_Lower'] = self.data['BB_Middle'] - (self.num_std * self.data['BB_Std'])

    def next(self, timestamp: pd.Timestamp, row: pd.Series):
        """
        Breakout logic: Buy when price breaks above Upper Band, Sell when below Lower Band.
        """
        if pd.isna(row.get('BB_Upper')) or pd.isna(row.get('BB_Lower')):
            return

        close = row['Close']

        # Buy signal: price breaks above upper band
        if close > row['BB_Upper'] and not self.position_open:
            self.buy(quantity=self.trade_qty)
            self.position_open = True

        # Sell signal: price breaks below lower band
        if close < row['BB_Lower'] and self.position_open:
            self.sell(quantity=self.trade_qty)
            self.position_open = False
