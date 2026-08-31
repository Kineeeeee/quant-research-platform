from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple


class MarketMaker:
    """
    Simple inventory-aware market maker. Quotes a bid and ask around the mid,
    earns the spread, and skews quotes to lean against its inventory so it
    doesn't accumulate a dangerous one-sided position.
    """

    def __init__(
        self,
        base_spread: float = 0.10,
        order_size: float = 100,
        max_inventory: float = 1000,
        inventory_skew: float = 0.5,
    ):
        self.base_spread = base_spread
        self.order_size = order_size
        self.max_inventory = max_inventory
        self.inventory_skew = inventory_skew

        self.inventory = 0.0
        self.cash = 0.0
        self.trades: List[Dict] = []

    def quote(self, mid_price: float) -> Tuple[float, float]:
        half_spread = self.base_spread / 2

        # skew the quotes against inventory: long -> shift both quotes down so
        # our ask is keener (more likely to sell) and bid is shy (less likely to
        # buy more). skew_adjustment is in [-1, 1] scaled by half the spread.
        skew_adjustment = (self.inventory / self.max_inventory) * self.inventory_skew * half_spread
        bid = mid_price - half_spread - skew_adjustment
        ask = mid_price + half_spread - skew_adjustment
        return bid, ask

    def on_fill(self, side: str, price: float, quantity: float):
        # inventory and cash move opposite ways: buy adds shares, spends cash;
        # sell removes shares, takes cash in
        if side == 'buy':
            self.inventory += quantity
            self.cash -= price * quantity
        elif side == 'sell':
            self.inventory -= quantity
            self.cash += price * quantity
        self.trades.append({'side': side, 'price': price, 'quantity': quantity})

    def pnl(self, current_mid: float) -> float:
        # mark-to-market: realised cash + inventory valued at the current mid
        return self.cash + self.inventory * current_mid

    def should_quote(self, side: str) -> bool:
        # stop quoting the side that would make inventory worse once we're at
        # the limit - still willing to trade the other way to flatten
        if side == 'buy' and self.inventory >= self.max_inventory:
            return False
        if side == 'sell' and self.inventory <= -self.max_inventory:
            return False
        return True
