import pandas as pd
import numpy as np
from typing import Dict, List, Optional
from src.analytics import metrics


class PerformanceReport:
    """Pulls equity curve + trade history into one summary, and compares strategies side by side."""

    def __init__(
        self,
        equity_curve: pd.DataFrame,
        trade_history: List[Dict],
        strategy_name: str = "Strategy",
        initial_capital: float = 100000.0,
    ):
        self.equity_curve = equity_curve
        self.trade_history = trade_history
        self.strategy_name = strategy_name
        self.initial_capital = initial_capital

    def calculate_all_metrics(self) -> Dict:
        returns = metrics.calculate_returns(self.equity_curve)

        return {
            'strategy_name': self.strategy_name,
            'initial_capital': self.initial_capital,
            'final_equity': self.equity_curve['equity'].iloc[-1],
            'total_return_pct': (self.equity_curve['equity'].iloc[-1] - self.initial_capital) / self.initial_capital * 100,
            'sharpe_ratio': metrics.sharpe_ratio(returns),
            'max_drawdown_pct': metrics.max_drawdown(self.equity_curve) * 100,
            'win_rate_pct': metrics.daily_win_rate(returns) * 100,
            'total_trades': len(self.trade_history),
            'start_date': str(self.equity_curve.index[0].date()),
            'end_date': str(self.equity_curve.index[-1].date()),
        }

    def calculate_trade_statistics(self) -> Dict:
        if not self.trade_history:
            return {}

        buy_trades = len([t for t in self.trade_history if t['direction'] == 'BUY'])
        sell_trades = len([t for t in self.trade_history if t['direction'] == 'SELL'])

        # P/L per round-trip: pair each BUY with the next SELL. assumes a flat
        # one-in-one-out position, which is how these strategies trade
        profits = []
        buy_price = None
        for t in self.trade_history:
            if t['direction'] == 'BUY':
                buy_price = t['price']
            elif t['direction'] == 'SELL' and buy_price is not None:
                pl = (t['price'] - buy_price) * t['quantity']
                profits.append(pl)
                buy_price = None

        if not profits:
            return {
                'buy_trades': buy_trades,
                'sell_trades': sell_trades,
                'avg_trade_return': 0.0,
                'max_win_trade': 0.0,
                'max_loss_trade': 0.0,
                'win_streak': 0,
                'loss_streak': 0,
            }

        avg_trade_return = np.mean(profits)
        max_win_trade = max(profits)
        max_loss_trade = min(profits)

        # Win/loss streaks
        win_streak = 0
        loss_streak = 0
        current_win = 0
        current_loss = 0
        for pl in profits:
            if pl > 0:
                current_win += 1
                current_loss = 0
                win_streak = max(win_streak, current_win)
            else:
                current_loss += 1
                current_win = 0
                loss_streak = max(loss_streak, current_loss)

        return {
            'buy_trades': buy_trades,
            'sell_trades': sell_trades,
            'avg_trade_return': avg_trade_return,
            'max_win_trade': max_win_trade,
            'max_loss_trade': max_loss_trade,
            'win_streak': win_streak,
            'loss_streak': loss_streak,
        }


    def calculate_annual_returns(self) -> pd.Series:
        yearly = self.equity_curve.resample('YE')
        returns = []
        for year, group in yearly:
            if len(group) >= 2:
                first_equity = group['equity'].iloc[0]
                last_equity = group['equity'].iloc[-1]
                annual_return = (last_equity - first_equity) / first_equity * 100
                returns.append((year.year, annual_return))
        return pd.Series(dict(returns))

    def print_report(self):
        m = self.calculate_all_metrics()
        print('=' * 45)
        print('     BACKTEST PERFORMANCE REPORT')
        print('=' * 45)
        print(f'  Strategy      : {m["strategy_name"]}')
        print(f'  Period        : {m["start_date"]} to {m["end_date"]}')
        print('-' * 45)
        print(f'  Initial Capital : ${m["initial_capital"]:,.0f}')
        print(f'  Final Equity    : ${m["final_equity"]:,.2f}')
        print(f'  Total Return    : {m["total_return_pct"]:+.2f}%')
        print(f'  Sharpe Ratio    : {m["sharpe_ratio"]:.2f}')
        print(f'  Max Drawdown    : {m["max_drawdown_pct"]:.2f}%')
        print(f'  Win Rate        : {m["win_rate_pct"]:.1f}%')
        print(f'  Total Trades    : {m["total_trades"]}')
        print('=' * 45)

    def to_dataframe(self) -> pd.DataFrame:
        # single row so several reports concat into a comparison table
        all_metrics = self.calculate_all_metrics()
        return pd.DataFrame([all_metrics])

    @staticmethod
    def compare_strategies(reports: List['PerformanceReport']) -> pd.DataFrame:
        dfs = [report.to_dataframe() for report in reports]
        return pd.concat(dfs, ignore_index=True)
