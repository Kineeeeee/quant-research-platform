import matplotlib.pyplot as plt
import pandas as pd


def plot_equity_curve(equity_curve: pd.DataFrame, title: str = "Strategy Equity Curve"):
    if equity_curve.empty:
        print("No data to plot.")
        return
    plt.plot(equity_curve.index, equity_curve['equity'])
    plt.title(title)
    plt.show()


def plot_drawdown(equity_curve: pd.DataFrame):
    peak = equity_curve['equity'].cummax()
    drawdown = (equity_curve['equity'] - peak) / peak
    plt.fill_between(drawdown.index, drawdown, 0, color='red', alpha=0.3)
    plt.title("Portfolio Drawdown")
    plt.show()
