import numpy as np
import pandas as pd

def calculate_returns(equity_curve: pd.DataFrame) -> pd.Series:
    """Calculate daily percentage returns from the 'equity' column."""
    data = equity_curve['equity'].pct_change().dropna()

    return data

def sharpe_ratio(returns: pd.Series, risk_free_rate: float = 0.0, periods_per_year: int = 252) -> float:
    """
    Calculate Sharpe Ratio (risk-adjusted return measure).
    """
    excess_returns = returns - risk_free_rate/ periods_per_year
    mean_returns = np.mean(excess_returns)
    std_returns = np.std(excess_returns)
    if std_returns == 0:
        return np.nan
    sharpe = (mean_returns/ std_returns) * np.sqrt(periods_per_year)

    return sharpe

def max_drawdown(equity_curve: pd.DataFrame) -> float:
    """
    Calculate Maximum Drawdown (largest peak-to-trough decline).
    """
    data = equity_curve['equity']
    peak = data.cummax()
    drawdown = (data - peak) / peak
    result = np.min(drawdown)
    return result

def daily_win_rate(returns: pd.Series) -> float:
    """
    Calculate daily win rate (fraction of profitable trading days).
    """
    wins = len(returns[returns > 0])
    total = len(returns[returns != 0])
    if total == 0:
        return 0.0
    return wins / total


def total_return(equity_curve: pd.DataFrame) -> float:
    """
    Compute total return percentage from equity curve.
    """
    first = equity_curve['equity'].iloc[0]
    last = equity_curve['equity'].iloc[-1]
    return (last - first) / first * 100
