import pandas as pd
from src.strategies.base import Strategy
import ta

class RSIReversion(Strategy):
    """
    Mean-reversion strategy using the RSI (Relative Strength Index).
    Buy when RSI enters the oversold zone (< 30).
    Sell when RSI enters the overbought zone (> 70).
    """
    def __init__(self, rsi_window: int = 14, overbought: int = 70, oversold: int = 30, trade_qty: float = 10):
        super().__init__()
        self.rsi_window = rsi_window
        self.overbought = overbought
        self.oversold = oversold
        self.trade_qty = trade_qty
        
        self.position_open = False
        
    def setup(self):
        """
        Compute RSI indicator on the full dataset (self.data).
        """
        self.data['RSI'] = ta.momentum.RSIIndicator(close=self.data['Close'], window=self.rsi_window).rsi()
        
    def next(self, timestamp: pd.Timestamp, row: pd.Series):
        """
        Make a trading decision for each bar.
        """
        if pd.isna(row.get('RSI')):
            return
            
        rsi_val = row.get('RSI')
        # Buy signal: RSI below oversold threshold
        if rsi_val < self.oversold and self.position_open == False:
            self.buy(quantity=self.trade_qty)
            self.position_open = True
        # Sell signal: RSI above overbought threshold
        if rsi_val > self.overbought and self.position_open == True:
            self.sell(quantity=self.trade_qty)
            self.position_open = False
        
        return
