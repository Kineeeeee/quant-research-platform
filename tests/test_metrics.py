import pytest
import pandas as pd
import numpy as np
from src.analytics.metrics import calculate_returns, sharpe_ratio, max_drawdown, daily_win_rate


class TestCalculateReturns:

    def test_basic_returns(self):
        equity_curve = pd.DataFrame({'equity': [100, 110, 121]})
        returns = calculate_returns(equity_curve)
        np.testing.assert_almost_equal(returns.values, [0.10, 0.10], decimal=6)

    def test_returns_with_loss(self):
        equity_curve = pd.DataFrame({'equity': [100, 90, 99]})
        returns = calculate_returns(equity_curve)
        np.testing.assert_almost_equal(returns.values, [-0.10, 0.10], decimal=6)

    def test_returns_no_nan(self):
        equity_curve = pd.DataFrame({'equity': [100, 105, 110]})
        returns = calculate_returns(equity_curve)
        assert not returns.isna().any()
        assert len(returns) == 2


class TestSharpeRatio:

    def test_positive_sharpe(self):
        returns = pd.Series([0.01, 0.02, 0.01, 0.015, 0.01])
        assert sharpe_ratio(returns) > 0

    def test_negative_sharpe(self):
        returns = pd.Series([-0.01, -0.02, -0.01, -0.015, -0.01])
        assert sharpe_ratio(returns) < 0

    def test_zero_std_returns_nan(self):
        # constant returns -> std 0, must not divide by zero
        returns = pd.Series([0.01, 0.01, 0.01, 0.01])
        assert np.isnan(sharpe_ratio(returns))

    def test_risk_free_rate_effect(self):
        returns = pd.Series([0.01, 0.02, 0.01, 0.015, 0.01])
        assert sharpe_ratio(returns, risk_free_rate=0.05) < sharpe_ratio(returns, risk_free_rate=0.0)


class TestMaxDrawdown:

    def test_known_drawdown(self):
        # 100 -> 120 -> 90: worst drop is (90-120)/120 = -25%
        equity_curve = pd.DataFrame({'equity': [100, 120, 90, 110]})
        assert max_drawdown(equity_curve) == pytest.approx(-0.25)

    def test_no_drawdown(self):
        equity_curve = pd.DataFrame({'equity': [100, 110, 120, 130]})
        assert max_drawdown(equity_curve) == pytest.approx(0.0)

    def test_full_drawdown(self):
        equity_curve = pd.DataFrame({'equity': [100, 50, 0]})
        assert max_drawdown(equity_curve) == pytest.approx(-1.0)

    def test_multiple_drawdowns_takes_worst(self):
        # peak 100 before the drop to 60 -> -40%
        equity_curve = pd.DataFrame({'equity': [100, 80, 90, 60, 70]})
        assert max_drawdown(equity_curve) == pytest.approx(-0.40)


class TestDailyWinRate:

    def test_basic_win_rate(self):
        returns = pd.Series([0.01, -0.02, 0.03, 0.01, -0.01])
        assert daily_win_rate(returns) == pytest.approx(0.6)

    def test_all_positive(self):
        assert daily_win_rate(pd.Series([0.01, 0.02, 0.03])) == pytest.approx(1.0)

    def test_all_negative(self):
        assert daily_win_rate(pd.Series([-0.01, -0.02, -0.03])) == pytest.approx(0.0)

    def test_all_zero_returns(self):
        assert daily_win_rate(pd.Series([0.0, 0.0, 0.0])) == 0.0

    def test_mixed_with_zero(self):
        # flat days excluded from the denominator: 2 wins / 3 non-flat
        returns = pd.Series([0.01, 0.0, -0.01, 0.02])
        assert daily_win_rate(returns) == pytest.approx(2.0 / 3.0)
