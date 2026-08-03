import pandas as pd
from src.strategies.base import Strategy

class SMACrossover(Strategy):
    """
    Simple Moving Average (SMA) Crossover strategy.
    Buy when short-term SMA crosses above long-term SMA.
    Sell when short-term SMA crosses below long-term SMA.
    """
    def __init__(self, short_window: int = 50, long_window: int = 200, trade_qty: float = 10):
        super().__init__()
        self.short_window = short_window
        self.long_window = long_window
        self.trade_qty = trade_qty
        
        # Track whether we currently hold a position
        self.position_open = False
        
    def setup(self):
        """
        Compute SMA indicators on the full dataset before running backtest.
        The dataset is stored in `self.data`.
        """
        self.data['SMA_Short'] = self.data['Close'].rolling(window=self.short_window).mean()
        self.data['SMA_Long'] = self.data['Close'].rolling(window=self.long_window).mean()
        
    def next(self, timestamp: pd.Timestamp, row: pd.Series):
        """
        Called for each bar (each day) in the historical data.
        `row` contains Open, High, Low, Close, SMA_Short, SMA_Long for the current day.
        """
        # Skip if SMAs don't have enough data yet
        if pd.isna(row.get('SMA_Short')) or pd.isna(row.get('SMA_Long')):
            return
            
        # Buy signal: short SMA crosses above long SMA
        if row.get('SMA_Short') > row.get('SMA_Long') and self.position_open == False:
            self.buy(quantity=self.trade_qty)
            self.position_open = True
        # Sell signal: long SMA crosses above short SMA
        if row.get('SMA_Long') > row.get('SMA_Short') and self.position_open == True:
            self.sell(quantity=self.trade_qty)
            self.position_open = False
