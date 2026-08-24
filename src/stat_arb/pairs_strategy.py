import pandas as pd
import numpy as np
from typing import Dict
from src.stat_arb.cointegration import CointegrationScanner


class PairsStrategy:
    """
    Mean-reversion on the spread of two cointegrated stocks. Short the spread
    when z is high (A rich vs B), long it when z is low, exit back at the mean.
    Long spread = buy A / sell B; short spread = sell A / buy B.
    """

    def __init__(
        self,
        ticker_a: str,
        ticker_b: str,
        entry_z: float = 2.0,
        exit_z: float = 0.0,
        stop_z: float = 4.0,
        lookback: int = 21,
    ):
        self.ticker_a = ticker_a
        self.ticker_b = ticker_b
        self.entry_z = entry_z
        self.exit_z = exit_z
        self.stop_z = stop_z
        self.lookback = lookback

    def backtest(self, prices: pd.DataFrame) -> Dict:
        scanner = CointegrationScanner(prices)
        data = scanner.compute_spread(self.ticker_a, self.ticker_b)
        spread = data['spread']
        z_score = data['z_score']
        position = 0
        num_trades = 0
        daily_pnl = []

        for i in range(1, len(spread)):
            z = z_score.iloc[i]
            pnl = 0

            # PnL accrues on yesterday's position before we react to today's z
            if position != 0:
                pnl = position * (spread.iloc[i] - spread.iloc[i - 1])

            if position == 0:
                if z < -self.entry_z:
                    position = 1
                    num_trades += 1
                elif z > self.entry_z:
                    position = -1
                    num_trades += 1
            elif position == 1:
                # exit at the mean, or bail if it keeps diverging past the stop
                if z >= self.exit_z or z < -self.stop_z:
                    position = 0
            elif position == -1:
                if z <= self.exit_z or z > self.stop_z:
                    position = 0

            daily_pnl.append(pnl)

        pnl_series = pd.Series(daily_pnl, index=spread.index[1:])
        equity_curve = pnl_series.cumsum()

        sharpe = pnl_series.mean() / pnl_series.std() * np.sqrt(252) if pnl_series.std() > 0 else 0
        max_dd = (equity_curve - equity_curve.cummax()).min()
        win_rate = (pnl_series[pnl_series != 0] > 0).mean() if (pnl_series != 0).any() else 0

        return {
            'equity_curve': equity_curve,
            'pnl_series': pnl_series,
            'sharpe': sharpe,
            'max_drawdown': max_dd,
            'num_trades': num_trades,
            'win_rate': win_rate,
        }

    def print_summary(self, result: Dict):
        print(f"\n=== Pairs Trading Summary ({self.ticker_a}/{self.ticker_b}) ===")
        print(f"Entry Z-Score: {self.entry_z}")
        print(f"Exit Z-Score: {self.exit_z}")
        print(f"Number of Trades: {result['num_trades']}")
        print(f"Sharpe Ratio: {result['sharpe']:.2f}")
        print(f"Max Drawdown: {result['max_drawdown']:.4f}")
        print(f"Win Rate: {result['win_rate']:.1%}")
