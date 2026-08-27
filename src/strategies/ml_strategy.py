import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from src.strategies.base import Strategy
import ta


class MLStrategy(Strategy):
    """
    Random forest predicting next-move direction, traded through the engine.

    CAVEAT: setup() trains on the whole series, so backtest results are
    optimistic (the model has seen the test period). The honest version is
    ml/pipeline.py with TimeSeriesSplit; this is the "wire ML into the engine"
    proof of concept. Would need a walk-forward retrain to trust the numbers.
    """

    def __init__(self, trade_qty: float = 10):
        super().__init__()
        self.trade_qty = trade_qty
        self.position_open = False
        self.entry_price = 0
        self.model = RandomForestClassifier(n_estimators=100, random_state=42)

    def setup(self):
        self.data['Return'] = self.data['Close'].pct_change()
        self.data['RSI'] = ta.momentum.RSIIndicator(self.data['Close'], window=14).rsi()
        self.data['SMA_Dist'] = self.data['Close'] / self.data['Close'].rolling(50).mean()

        # target = up 2 days out. shift(-2) vs shift(-1) so we're predicting the
        # move we could actually act on, not today's already-known bar
        self.data['Target'] = np.where(self.data['Close'].shift(-2) > self.data['Close'].shift(-1), 1, 0)

        self.data.dropna(inplace=True)
        features = ['Return', 'RSI', 'SMA_Dist']
        self.model.fit(self.data[features], self.data['Target'])

    def next(self, timestamp: pd.Timestamp, row: pd.Series):
        current_features = pd.DataFrame(
            [[row.get('Return'), row.get('RSI'), row.get('SMA_Dist')]],
            columns=['Return', 'RSI', 'SMA_Dist'],
        )
        prediction = self.model.predict(current_features)[0]

        if prediction == 1 and not self.position_open:
            self.current_qty = int((self.portfolio.cash * 0.9) / row.get('Close'))
            self.buy(quantity=self.current_qty)
            self.position_open = True
            self.entry_price = row.get('Close')

        # hard 5% stop - the model has no risk sense of its own
        if self.position_open and row.get('Close') <= self.entry_price * 0.95:
            self.sell(quantity=self.current_qty)
            self.position_open = False
            return

        if prediction == 0 and self.position_open:
            self.sell(quantity=self.current_qty)
            self.position_open = False
