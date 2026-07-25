from typing import List
from src.backtest.order import Order, OrderType, OrderDirection
import pandas as pd

class Strategy:
    """
    Base Strategy class. 
    Users should inherit from this class to build their own strategies.
    """
    def __init__(self):
        self.data: pd.DataFrame = None
        self.orders: List[Order] = []
        self.ticker: str = "ASSET"
        
    def init(self, data: pd.DataFrame, ticker: str = "ASSET"):
        """
        Called once before the backtest starts.
        Used to calculate indicators and setup the strategy.
        """
        self.data = data
        self.ticker = ticker
        self.setup()
        
    def setup(self):
        """Override this to compute indicators on self.data"""
        pass
        
    def next(self, timestamp: pd.Timestamp, row: pd.Series):
        """
        Called on every bar/row of the data.
        Override this to implement trading logic.
        """
        raise NotImplementedError("Strategy must implement next()")
        
    def buy(self, quantity: float, price: float = None):
        """Helper to create a BUY order"""
        order_type = OrderType.MARKET if price is None else OrderType.LIMIT
        order = Order(self.ticker, OrderDirection.BUY, quantity, order_type, price)
        self.orders.append(order)
        
    def sell(self, quantity: float, price: float = None):
        """Helper to create a SELL order"""
        order_type = OrderType.MARKET if price is None else OrderType.LIMIT
        order = Order(self.ticker, OrderDirection.SELL, quantity, order_type, price)
        self.orders.append(order)
