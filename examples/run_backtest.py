"""Run a complete backtest pipeline: data → strategy → engine → metrics → plot."""
import sys
from pathlib import Path

project_root = str(Path(__file__).resolve().parent.parent)
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from src.data.loader import DataLoader
from src.data.cleaner import DataCleaner
from src.strategies.momentum import SMACrossover
from src.backtest.engine import BacktestEngine
from src.analytics import metrics


def main():
    ticker = "AAPL"
    start_date = "2020-01-01"
    end_date = "2023-12-31"

    print(f"--- RUNNING BACKTEST FOR {ticker} ---")

    raw_data = DataLoader.fetch_historical_data(ticker, start_date, end_date)
    DataLoader.save_raw_data(raw_data, ticker)
    cleaned_data = DataCleaner.clean_data(ticker)
    DataCleaner.save_processed_data(cleaned_data, ticker)

    strategy = SMACrossover(short_window=50, long_window=200, trade_qty=10)

    engine = BacktestEngine(cleaned_data, strategy, initial_capital=100000)
    equity_curve = engine.run()

    returns = metrics.calculate_returns(equity_curve)
    sharpe = metrics.sharpe_ratio(returns)
    drawdown = metrics.max_drawdown(equity_curve)
    win_rate = metrics.daily_win_rate(returns)

    print(f"Sharpe Ratio: {sharpe:.2f}")
    print(f"Max Drawdown: {drawdown * 100:.2f}%")
    print(f"Win Rate: {win_rate * 100:.2f}%")


if __name__ == "__main__":
    main()
