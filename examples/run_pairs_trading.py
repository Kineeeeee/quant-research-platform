# Scan a universe for cointegrated pairs, then backtest the best one.
import sys
sys.path.insert(0, '.')

import yfinance as yf
from src.stat_arb.cointegration import CointegrationScanner
from src.stat_arb.pairs_strategy import PairsStrategy

TICKERS = ['KO', 'PEP', 'V', 'MA', 'XOM', 'CVX', 'JPM', 'BAC', 'AAPL', 'MSFT']

raw = yf.download(TICKERS, start='2018-01-01', end='2024-12-31', auto_adjust=True, progress=False)
prices = raw['Close'].dropna(axis=1, how='all').ffill()

print(f'Universe: {list(prices.columns)}')
print(f'Period: {prices.index[0].date()} to {prices.index[-1].date()}')
print()

# Step 1: Find cointegrated pairs
print('=== SCANNING FOR COINTEGRATED PAIRS ===')
scanner = CointegrationScanner(prices)
pairs = scanner.find_pairs(p_threshold=0.05)

if len(pairs) == 0:
    print('No cointegrated pairs found.')
else:
    print(f'Found {len(pairs)} cointegrated pairs:')
    print(pairs.to_string(index=False))
    print()

    # Step 2: Analyze best pair
    best = pairs.iloc[0]
    print(f'=== ANALYZING BEST PAIR: {best["ticker_a"]} / {best["ticker_b"]} ===')

    # Compute spread
    spread_df = scanner.compute_spread(best['ticker_a'], best['ticker_b'])
    print(f'Hedge ratio (beta): {spread_df["beta"].iloc[0]:.4f}')

    # Half-life
    hl = scanner.compute_half_life(spread_df['spread'])
    print(f'Half-life: {hl:.1f} days')
    print()

    # Step 3: Backtest pairs strategy
    print('=== PAIRS TRADING BACKTEST ===')
    ps = PairsStrategy(best['ticker_a'], best['ticker_b'], entry_z=2.0, exit_z=0.0)
    result = ps.backtest(prices)
    ps.print_summary(result)
