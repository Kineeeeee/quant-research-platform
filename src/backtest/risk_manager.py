import pandas as pd
from src.backtest.order import Order, OrderDirection
from src.backtest.portfolio import Portfolio


class RiskManager:
    """Vetoes orders that break position/risk/drawdown limits before they fill."""

    def __init__(
        self,
        max_position_pct: float = 0.20,
        max_portfolio_risk_pct: float = 0.02,
        max_drawdown_limit: float = 0.25,
        max_open_positions: int = 5,
    ):
        self.max_position_pct = max_position_pct
        self.max_portfolio_risk_pct = max_portfolio_risk_pct
        self.max_drawdown_limit = max_drawdown_limit
        self.max_open_positions = max_open_positions
        self.peak_equity = 0.0

    def check_order(self, order: Order, portfolio: Portfolio, current_price: float) -> bool:
        # selling only reduces exposure, always allow it
        if order.direction == OrderDirection.SELL:
            return True

        position_value = sum(qty * current_price for qty in portfolio.positions.values())
        total_equity = portfolio.cash + position_value

        order_value = order.quantity * current_price
        if order_value / total_equity > self.max_position_pct:
            return False

        num = sum(1 for qty in portfolio.positions.values() if qty > 0)
        if num >= self.max_open_positions:
            return False

        # drawdown circuit breaker: stop opening new risk after a big peak-to-now drop
        if total_equity > self.peak_equity:
            self.peak_equity = total_equity
        current_drawdown = 0 if self.peak_equity == 0 else (total_equity - self.peak_equity) / self.peak_equity
        if current_drawdown < -self.max_drawdown_limit:
            return False

        # 2% rule: assume a 5% stop, cap the loss it implies at max_portfolio_risk_pct of equity
        risk_per_share = current_price * 0.05
        if (risk_per_share * order.quantity) / total_equity > self.max_portfolio_risk_pct:
            return False

        return True

    def calculate_position_size(self, portfolio: Portfolio, current_price: float, stop_loss_pct: float = 0.05) -> int:
        """Fixed-fractional sizing: smaller of the 2%-risk size and the concentration cap."""
        position_value = sum(qty * current_price for qty in portfolio.positions.values())
        total_equity = portfolio.cash + position_value
        max_risk_amount = total_equity * self.max_portfolio_risk_pct
        risk_per_share = current_price * stop_loss_pct
        quantity_by_risk = int(max_risk_amount / risk_per_share)
        quantity_by_limit = int(total_equity * self.max_position_pct / current_price)
        return min(quantity_by_risk, quantity_by_limit)

    def calculate_vol_adjusted_size(
        self,
        portfolio: Portfolio,
        current_price: float,
        current_vol: float,
        vol_target: float = 0.10,
    ) -> int:
        """Scale the base size by vol_target / current_vol so high-vol names get smaller positions."""
        base_size = self.calculate_position_size(portfolio, current_price)
        if current_vol <= 0 or pd.isna(current_vol):
            return base_size
        vol_scalar = max(0.25, min(2.0, vol_target / current_vol))   # cap 0.25x - 2x
        return max(1, int(base_size * vol_scalar))
