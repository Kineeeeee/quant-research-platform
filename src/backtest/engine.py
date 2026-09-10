import logging
import pandas as pd
from src.backtest.portfolio import Portfolio
from src.backtest.order import OrderStatus
from src.backtest.risk_manager import RiskManager
from src.strategies.base import Strategy

logger = logging.getLogger(__name__)


class BacktestEngine:
    def __init__(self, data: pd.DataFrame, strategy: Strategy, initial_capital: float = 100000.0,
                 ticker: str = "ASSET", risk_manager: RiskManager = None):
        self.data = data
        self.strategy = strategy
        self.portfolio = Portfolio(initial_capital)
        self.ticker = ticker
        self.risk_manager = risk_manager if risk_manager else RiskManager()

    def run(self) -> pd.DataFrame:
        self.strategy.portfolio = self.portfolio
        self.strategy.init(self.data, self.ticker)
        logger.info("Starting backtest loop...")

        for timestamp, row in self.data.iterrows():
            current_price = row['Close']

            for order in self.strategy.orders:
                if order.status == OrderStatus.PENDING and order.order_type.value == 'MARKET':
                    order.filled_price = current_price
                    # take risk manager right before an order fills
                    if not self.risk_manager.check_order(order, self.portfolio, current_price):
                        order.status = OrderStatus.REJECTED
                        continue
                    order.status = OrderStatus.FILLED
                    self.portfolio.execute_order(order, timestamp)

            self.strategy.orders = [o for o in self.strategy.orders if o.status == OrderStatus.PENDING]
            self.strategy.next(timestamp, row)
            self.portfolio.update_equity(timestamp, {self.ticker: current_price})

        logger.info("Backtest completed.")
        return self.portfolio.get_equity_curve()
