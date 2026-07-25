import logging
from typing import Dict
import pandas as pd

logger = logging.getLogger(__name__)

class Portfolio:
    """
    Manages capital, stock positions, and computes total equity.
    """
    def __init__(self, initial_capital: float = 100000.0, commission_rate: float = 0.001, slippage: float = 0.0005):
        """
        Initialize portfolio.
        - commission_rate: 0.001 = 0.1% transaction fee per trade.
        - slippage: 0.0005 = 0.05% price impact from latency or liquidity.
        """
        self.cash = initial_capital
        self.commission_rate = commission_rate
        self.slippage = slippage
        self.positions: Dict[str, float] = {}  # Shares held per ticker (e.g. {'AAPL': 50})
        self.equity_history = []
        self.trade_history = []

    def execute_order(self, order, timestamp: pd.Timestamp):
        """
        Execute a trade order, adjusting cash and positions with realistic slippage and commission.
        """
        if order.filled_price is None:
            return False
            
        if order.direction.value == 'BUY':
            # Slippage makes effective buy price slightly higher
            real_price = order.filled_price * (1 + self.slippage)
            commission = real_price * order.quantity * self.commission_rate
            total = (real_price * order.quantity) + commission
            if self.cash < total:
                return False
            self.cash -= total
            self.positions[order.ticker] = self.positions.get(order.ticker, 0) + order.quantity
        elif order.direction.value == 'SELL':
            # Slippage makes effective sell price slightly lower
            real_price = order.filled_price * (1 - self.slippage)
            commission = real_price * order.quantity * self.commission_rate
            total = (real_price * order.quantity) - commission
            if self.positions.get(order.ticker, 0) < order.quantity:
                return False
            self.cash += total
            self.positions[order.ticker] -= order.quantity

        # Record trade history
        self.trade_history.append({
            'timestamp': timestamp,
            'ticker': order.ticker,
            'direction': order.direction.value,
            'quantity': order.quantity,
            'price': order.filled_price,
            'cash_after': self.cash
        })
        
        return True

    def update_equity(self, timestamp: pd.Timestamp, current_prices: Dict[str, float]):
        """
        Compute total portfolio equity at the current timestamp.
        Total equity = cash + sum(shares * current_price) for all positions.
        """
        total = sum([qty * current_prices[ticker] for ticker, qty in self.positions.items()])
        total_equity = self.cash + total
        self.equity_history.append({
            'timestamp': timestamp,
            'equity': total_equity
        })

    def get_equity_curve(self) -> pd.DataFrame:
        """
        Return equity curve as a DataFrame.
        """
        if not self.equity_history:
            return pd.DataFrame()
            
        df = pd.DataFrame(self.equity_history)
        df.set_index('timestamp', inplace=True)
        return df
