import pandas as pd
import numpy as np
from src.strategies.momentum import SMACrossover
from src.strategies.rsi import RSIReversion
from src.backtest.order import OrderDirection


class TestSMACrossover:

    def _create_sample_data(self, n_days=250):
        np.random.seed(42)
        dates = pd.date_range("2020-01-01", periods=n_days)
        close = 100 + np.cumsum(np.random.randn(n_days) * 2)
        open_ = np.concatenate(([close[0]], close[:-1])) + np.random.randn(n_days) * 0.5
        high = np.maximum(open_, close) + np.random.rand(n_days)
        low = np.minimum(open_, close) - np.random.rand(n_days)
        volume = np.random.randint(100000, 1000000, size=n_days)
        return pd.DataFrame({
            "Open": open_, "High": high, "Low": low, "Close": close, "Volume": volume,
        }, index=dates)

    def test_setup_creates_sma_columns(self):
        strategy = SMACrossover(short_window=10, long_window=50)
        strategy.init(self._create_sample_data(), 'TEST')
        assert 'SMA_Short' in strategy.data.columns
        assert 'SMA_Long' in strategy.data.columns

    def test_no_signal_when_sma_nan(self):
        # data shorter than long_window -> SMA_Long all NaN -> no orders
        data = self._create_sample_data(n_days=10)
        strategy = SMACrossover(short_window=5, long_window=50)
        strategy.init(data, 'TEST')
        for timestamp, row in strategy.data.iterrows():
            strategy.next(timestamp, row)
        assert strategy.orders == []

    def test_buy_signal_on_golden_cross(self):
        # sideways then a sharp rise pushes short SMA above long SMA
        prices = np.concatenate([np.full(60, 100.0) + np.random.randn(60) * 0.1,
                                 np.linspace(100, 130, 20)])
        dates = pd.date_range("2020-01-01", periods=len(prices))
        df = pd.DataFrame({"Open": prices, "High": prices + 1, "Low": prices - 1,
                           "Close": prices, "Volume": 500000}, index=dates)
        strategy = SMACrossover(short_window=5, long_window=20)
        strategy.init(df, 'TEST')
        for timestamp, row in strategy.data.iterrows():
            strategy.next(timestamp, row)
        buy_orders = [o for o in strategy.orders if o.direction == OrderDirection.BUY]
        assert len(buy_orders) >= 1

    def test_sell_signal_on_death_cross(self):
        # rise (to open a long) then a sharp drop -> death cross
        prices = np.concatenate([np.linspace(100, 130, 40), np.full(20, 130.0),
                                 np.linspace(130, 95, 40)])
        dates = pd.date_range("2020-01-01", periods=len(prices))
        df = pd.DataFrame({"Open": prices, "High": prices + 1, "Low": prices - 1,
                           "Close": prices, "Volume": 500000}, index=dates)
        strategy = SMACrossover(short_window=5, long_window=20)
        strategy.init(df, 'TEST')
        for timestamp, row in strategy.data.iterrows():
            strategy.next(timestamp, row)
        sell_orders = [o for o in strategy.orders if o.direction == OrderDirection.SELL]
        assert len(sell_orders) >= 1

    def test_no_double_buy(self):
        strategy = SMACrossover(short_window=10, long_window=50)
        strategy.init(self._create_sample_data(n_days=300), 'TEST')
        for timestamp, row in strategy.data.iterrows():
            strategy.next(timestamp, row)
        for i in range(1, len(strategy.orders)):
            if strategy.orders[i].direction == OrderDirection.BUY:
                assert strategy.orders[i - 1].direction == OrderDirection.SELL


class TestRSIReversion:

    def _create_declining_data(self, n_days=50):
        dates = pd.date_range("2020-01-01", periods=n_days)
        prices = np.linspace(100, 50, n_days)
        return pd.DataFrame({"Open": prices + 1, "High": prices + 2, "Low": prices - 1,
                             "Close": prices, "Volume": 500000}, index=dates)

    def _create_rising_data(self, n_days=50):
        dates = pd.date_range("2020-01-01", periods=n_days)
        prices = np.linspace(50, 150, n_days)
        return pd.DataFrame({"Open": prices - 1, "High": prices + 1, "Low": prices - 2,
                             "Close": prices, "Volume": 500000}, index=dates)

    def test_buy_on_oversold(self):
        strategy = RSIReversion(rsi_window=14, oversold=30, overbought=70)
        strategy.init(self._create_declining_data(), 'TEST')
        for timestamp, row in strategy.data.iterrows():
            strategy.next(timestamp, row)
        buy_orders = [o for o in strategy.orders if o.direction == OrderDirection.BUY]
        assert len(buy_orders) >= 1

    def test_sell_on_overbought(self):
        strategy = RSIReversion(rsi_window=14, oversold=30, overbought=70)
        strategy.init(self._create_rising_data(), 'TEST')
        strategy.position_open = True   # pretend we're already long
        for timestamp, row in strategy.data.iterrows():
            strategy.next(timestamp, row)
        sell_orders = [o for o in strategy.orders if o.direction == OrderDirection.SELL]
        assert len(sell_orders) >= 1

    def test_no_double_buy(self):
        np.random.seed(123)
        n = 150
        dates = pd.date_range("2020-01-01", periods=n)
        prices = np.maximum(100 + np.cumsum(np.random.randn(n) * 3), 10)
        df = pd.DataFrame({"Open": prices, "High": prices + 2, "Low": prices - 2,
                           "Close": prices, "Volume": 500000}, index=dates)
        strategy = RSIReversion(rsi_window=14, oversold=30, overbought=70)
        strategy.init(df, 'TEST')
        for timestamp, row in strategy.data.iterrows():
            strategy.next(timestamp, row)
        for i in range(1, len(strategy.orders)):
            if strategy.orders[i].direction == OrderDirection.BUY:
                assert strategy.orders[i - 1].direction == OrderDirection.SELL

    def test_no_signal_when_rsi_nan(self):
        dates = pd.date_range("2020-01-01", periods=5)
        prices = [100, 99, 98, 97, 96]
        df = pd.DataFrame({"Open": prices, "High": prices, "Low": prices,
                           "Close": prices, "Volume": 500000}, index=dates)
        strategy = RSIReversion(rsi_window=14, oversold=30, overbought=70)
        strategy.init(df, 'TEST')
        for timestamp, row in strategy.data.iterrows():
            strategy.next(timestamp, row)
        assert strategy.orders == []
