import numpy as np
import pandas as pd
from typing import Dict, List
from src.execution.order_book import OrderBook
from src.execution.market_maker import MarketMaker


class MarketSimulator:
    """
    Toy market: an order book, one market maker posting two-sided quotes, and
    noise traders sending random market orders. Runs tick-by-tick and tracks
    the price, spread, and the market maker's inventory and PnL.
    """

    def __init__(
        self,
        initial_mid: float = 100.0,
        n_steps: int = 1000,
        volatility: float = 0.001,
        noise_intensity: float = 0.3,
    ):
        self.initial_mid = initial_mid
        self.n_steps = n_steps
        self.volatility = volatility
        self.noise_intensity = noise_intensity
        self.ob = OrderBook()
        self.mm: MarketMaker = None

    def add_market_maker(self, **kwargs):
        self.mm = MarketMaker(**kwargs)

    def run(self) -> Dict:
        mid_price = self.initial_mid
        price_series = []
        spread_series = []
        inventory_series = []

        for _ in range(self.n_steps):
            # fresh book each tick: the MM is the only resting liquidity, so
            # clear and repost rather than cancel/replace individual orders
            self.ob = OrderBook()
            bid, ask = self.mm.quote(mid_price)
            if self.mm.should_quote('buy'):
                self.ob.add_limit_order('buy', round(bid, 2), self.mm.order_size, 'mm')
            if self.mm.should_quote('sell'):
                self.ob.add_limit_order('sell', round(ask, 2), self.mm.order_size, 'mm')

            # noise trader hits the book at random; whichever side it takes, the
            # MM is the counterparty, so feed that fill back to update inventory
            if np.random.rand() < self.noise_intensity:
                side = 'buy' if np.random.rand() > 0.5 else 'sell'
                size = np.random.randint(10, 50)
                fills = self.ob.add_market_order(side, size, trader_id='noise')
                for t in fills:
                    # noise buys -> MM sold; noise sells -> MM bought
                    self.mm.on_fill('sell' if side == 'buy' else 'buy', t.price, t.quantity)

            mid_price += self.volatility * np.random.randn()
            price_series.append(mid_price)
            spread_series.append(self.mm.base_spread)
            inventory_series.append(self.mm.inventory)

        return {
            'price_series': price_series,
            'spread_series': spread_series,
            'mm_inventory': inventory_series,
            'mm_pnl': self.mm.pnl(mid_price),
            'trades': self.mm.trades,
        }

    def print_summary(self, results: Dict):
        prices = results['price_series']
        spreads = results['spread_series']
        trades = results['trades']
        inv = results['mm_inventory']

        print('=' * 50)
        print('       MARKET SIMULATION SUMMARY')
        print('=' * 50)
        print(f'  Total ticks      : {self.n_steps}')
        print(f'  MM trades        : {len(trades)}')
        print(f'  Avg spread       : {np.mean(spreads):.4f}')
        print('-' * 50)
        print(f'  Price start      : ${prices[0]:.2f}')
        print(f'  Price end        : ${prices[-1]:.2f}')
        print(f'  Price range      : ${min(prices):.2f} - ${max(prices):.2f}')
        print('-' * 50)
        print(f'  MM final PnL     : ${results["mm_pnl"]:.2f}')
        print(f'  MM final inventory: {inv[-1]}')
        print(f'  MM max inventory : {max(inv)}')
        print(f'  MM min inventory : {min(inv)}')
        print('=' * 50)
