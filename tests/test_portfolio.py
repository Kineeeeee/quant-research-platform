import pytest
import pandas as pd
from src.backtest.portfolio import Portfolio
from src.backtest.order import Order, OrderType, OrderDirection


class TestPortfolio:

    def setup_method(self):
        self.portfolio = Portfolio(initial_capital=100000.0)

    def _make_order(self, direction, quantity, price, ticker='AAPL'):
        order = Order(ticker=ticker, direction=direction, quantity=quantity,
                      order_type=OrderType.MARKET)
        order.filled_price = price   # engine sets this on fill
        return order

    def test_initial_state(self):
        assert self.portfolio.cash == 100000.0
        assert self.portfolio.positions == {}
        assert len(self.portfolio.equity_history) == 0

    def test_buy_order_success(self):
        order = self._make_order(OrderDirection.BUY, 10, 100.0)
        result = self.portfolio.execute_order(order, pd.Timestamp('2020-01-02'))

        assert result is True
        assert self.portfolio.positions['AAPL'] == 10
        # price 100 * (1 + 0.0005 slippage) = 100.05; commission 100.05*10*0.001 = 1.0005
        expected_cash = 100000.0 - (100.05 * 10 + 1.0005)
        assert self.portfolio.cash == pytest.approx(expected_cash, rel=1e-6)

    def test_sell_order_success(self):
        self.portfolio.positions = {'AAPL': 10}
        order = self._make_order(OrderDirection.SELL, 10, 150.0)
        result = self.portfolio.execute_order(order, pd.Timestamp('2020-02-01'))

        assert result is True
        assert self.portfolio.positions['AAPL'] == 0
        assert self.portfolio.cash > 100000.0

    def test_buy_insufficient_cash(self):
        order = self._make_order(OrderDirection.BUY, 10000, 100.0)
        result = self.portfolio.execute_order(order, pd.Timestamp('2020-01-02'))

        assert result is False
        assert self.portfolio.cash == 100000.0
        assert self.portfolio.positions == {}

    def test_sell_no_position(self):
        order = self._make_order(OrderDirection.SELL, 10, 100.0)
        assert self.portfolio.execute_order(order, pd.Timestamp('2020-01-02')) is False

    def test_update_equity(self):
        self.portfolio.positions = {'AAPL': 50}
        self.portfolio.cash = 50000.0
        self.portfolio.update_equity(pd.Timestamp('2020-03-01'), current_prices={'AAPL': 200.0})

        assert len(self.portfolio.equity_history) == 1
        assert self.portfolio.equity_history[0]['equity'] == 60000.0
