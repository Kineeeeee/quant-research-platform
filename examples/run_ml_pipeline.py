# ML pipeline on AAPL 1-month forward returns: Ridge vs Random Forest.
import sys
sys.path.insert(0, '.')
import yfinance as yf
from src.ml.pipeline import MLPipeline

data = yf.download('AAPL', start='2015-01-01', end='2024-12-31', auto_adjust=True, progress=False)
prices = data['Close'].squeeze()

print(f'AAPL: {len(prices)} days ({prices.index[0].date()} to {prices.index[-1].date()})')
print()

print('=== ML Pipeline: Ridge Regression ===')
pipe_ridge = MLPipeline(prices, model_type='ridge', forward_period=21, n_splits=5)
result_ridge = pipe_ridge.run()
pipe_ridge.print_summary(result_ridge)
print()

print('=== ML Pipeline: Random Forest ===')
pipe_rf = MLPipeline(prices, model_type='random_forest', forward_period=21, n_splits=5)
result_rf = pipe_rf.run()
pipe_rf.print_summary(result_rf)
