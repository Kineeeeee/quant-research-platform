# Run a tick-by-tick LOB simulation with an inventory-aware market maker.
import sys
sys.path.insert(0, '.')

from src.execution.simulator import MarketSimulator

sim = MarketSimulator(initial_mid=100.0, n_steps=5000, volatility=0.002)
sim.add_market_maker(base_spread=0.10, order_size=100, max_inventory=500)

print('=== LOB MARKET SIMULATION ===')
print(f'Ticks: {sim.n_steps}')
print(f'Initial mid: ${sim.initial_mid}')
print()

results = sim.run()
sim.print_summary(results)
