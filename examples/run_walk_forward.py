# Walk-forward SMACrossover vs VolAdjustedMomentum - which one holds up OOS?
import sys
sys.path.insert(0, '.')

from src.data.loader import DataLoader
from src.data.cleaner import DataCleaner
from src.strategies.momentum import SMACrossover
from src.strategies.vol_momentum import VolAdjustedMomentum
from src.analytics.walk_forward import WalkForwardAnalyzer

# Load longer data for walk-forward (need at least 4 years)
data = DataLoader.fetch_historical_data('AAPL', '2018-01-01', '2023-12-31')
DataLoader.save_raw_data(data, 'AAPL')
clean = DataCleaner.clean_data('AAPL')

print(f'Data: {len(clean)} days ({clean.index[0].date()} to {clean.index[-1].date()})')
print()

# ============================================================
# Walk-Forward: SMACrossover
# ============================================================
print('=' * 55)
print('  WALK-FORWARD: SMACrossover (short=50, long=200)')
print('=' * 55)

wf_sma = WalkForwardAnalyzer(
    data=clean,
    strategy_class=SMACrossover,
    train_period_days=504,   # 2 years train
    test_period_days=252,    # 1 year test
    step_days=252,           # slide 1 year
)

result_sma = wf_sma.run(strategy_params={'short_window': 50, 'long_window': 200})

print(f"  Windows tested  : {result_sma['total_windows']}")
print(f"  Avg OOS Sharpe  : {result_sma['avg_sharpe']:.2f}")
print(f"  Worst Sharpe    : {result_sma['worst_sharpe']:.2f}")
print(f"  Consistency     : {result_sma['consistency']:.0f}% windows profitable")
print()
print(result_sma['results'].to_string(index=False))
print()

# ============================================================
# Walk-Forward: VolAdjustedMomentum (best params from tuning)
# ============================================================
print('=' * 55)
print('  WALK-FORWARD: VolAdjustedMomentum (short=10, long=50)')
print('=' * 55)

wf_vol = WalkForwardAnalyzer(
    data=clean,
    strategy_class=VolAdjustedMomentum,
    train_period_days=504,
    test_period_days=252,
    step_days=252,
)

result_vol = wf_vol.run(strategy_params={'short_window': 10, 'long_window': 50, 'vol_filter_mult': 2.5, 'base_qty': 25})

print(f"  Windows tested  : {result_vol['total_windows']}")
print(f"  Avg OOS Sharpe  : {result_vol['avg_sharpe']:.2f}")
print(f"  Worst Sharpe    : {result_vol['worst_sharpe']:.2f}")
print(f"  Consistency     : {result_vol['consistency']:.0f}% windows profitable")
print()
print(result_vol['results'].to_string(index=False))
print()

# ============================================================
# Comparison
# ============================================================
print('=' * 55)
print('  COMPARISON')
print('=' * 55)
print(f"  {'Strategy':<25} {'Avg Sharpe':>10} {'Worst':>7} {'Consistency':>12}")
print(f"  {'-'*25} {'-'*10} {'-'*7} {'-'*12}")
print(f"  {'SMACrossover':<25} {result_sma['avg_sharpe']:>10.2f} {result_sma['worst_sharpe']:>7.2f} {result_sma['consistency']:>10.0f}%")
print(f"  {'VolAdjustedMomentum':<25} {result_vol['avg_sharpe']:>10.2f} {result_vol['worst_sharpe']:>7.2f} {result_vol['consistency']:>10.0f}%")
print()

if result_vol['avg_sharpe'] > result_sma['avg_sharpe']:
    print('  -> VolAdjustedMomentum outperforms on average.')
else:
    print('  -> SMACrossover outperforms on average.')

if result_vol['worst_sharpe'] > result_sma['worst_sharpe']:
    print('  -> VolAdjustedMomentum has better worst-case (more robust).')
else:
    print('  -> SMACrossover has better worst-case.')
