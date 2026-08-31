import heapq
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Tuple
from datetime import datetime


@dataclass
class BookOrder:
    price: float
    quantity: float
    side: str           # 'buy' or 'sell'
    trader_id: str
    timestamp: datetime = field(default_factory=datetime.now)
    order_id: int = 0


@dataclass
class Trade:
    price: float
    quantity: float
    buyer_id: str
    seller_id: str
    timestamp: datetime = field(default_factory=datetime.now)


class OrderBook:
    """
    Central limit order book. Bids sorted high->low, asks low->high; a market
    order eats the best-priced resting orders first. Price-time priority.
    """

    def __init__(self):
        # both sides are heaps for O(log n) best-price access. python's heapq is
        # a min-heap, so bids store -price to fake a max-heap; ts is the
        # tiebreaker so earlier orders at the same price fill first (time priority)
        self.bids: List = []   # (neg_price, timestamp, order)
        self.asks: List = []   # (price, timestamp, order)
        self.trades: List[Trade] = []
        self._order_counter = 0

    def add_limit_order(self, side: str, price: float, quantity: float, trader_id: str) -> List[Trade]:
        if side == 'buy':
            trades = []
            # cross against asks while our bid is at or above the best ask
            while quantity > 0 and len(self.asks) > 0 and self.best_ask() <= price:
                ask_price, ask_ts, ask_order = heapq.heappop(self.asks)
                trade_qty = min(quantity, ask_order.quantity)
                trades.append(Trade(ask_price, trade_qty, trader_id, ask_order.trader_id))
                quantity -= trade_qty
                ask_order.quantity -= trade_qty
                # partially-filled resting order goes back on the book
                if ask_order.quantity > 0:
                    heapq.heappush(self.asks, (ask_price, ask_ts, ask_order))
            if quantity > 0:
                self._order_counter += 1
                order = BookOrder(price, quantity, side, trader_id, order_id=self._order_counter)
                heapq.heappush(self.bids, (-price, order.timestamp, order))
            return trades

        elif side == 'sell':
            trades = []
            while quantity > 0 and len(self.bids) > 0 and self.best_bid() >= price:
                bid_price, bid_ts, bid_order = heapq.heappop(self.bids)
                real_price = -bid_price
                trade_qty = min(quantity, bid_order.quantity)
                trades.append(Trade(real_price, trade_qty, bid_order.trader_id, trader_id))
                quantity -= trade_qty
                bid_order.quantity -= trade_qty
                if bid_order.quantity > 0:
                    heapq.heappush(self.bids, (bid_price, bid_ts, bid_order))
            if quantity > 0:
                self._order_counter += 1
                order = BookOrder(price, quantity, side, trader_id, order_id=self._order_counter)
                heapq.heappush(self.asks, (price, order.timestamp, order))
            return trades
        else:
            raise ValueError("Side must be 'buy' or 'sell'")

    def add_market_order(self, side: str, quantity: float, trader_id: str) -> List[Trade]:
        # a market order is just a limit order that crosses everything, so it
        # walks the book taking whatever price is there (no price guard)
        if side == 'buy':
            trades = []
            while quantity > 0 and len(self.asks) > 0:
                ask_price, ask_ts, ask_order = heapq.heappop(self.asks)
                trade_qty = min(quantity, ask_order.quantity)
                trades.append(Trade(ask_price, trade_qty, trader_id, ask_order.trader_id))
                quantity -= trade_qty
                ask_order.quantity -= trade_qty
                if ask_order.quantity > 0:
                    heapq.heappush(self.asks, (ask_price, ask_ts, ask_order))
            self.trades.extend(trades)
            return trades
        elif side == 'sell':
            trades = []
            while quantity > 0 and len(self.bids) > 0:
                bid_price, bid_ts, bid_order = heapq.heappop(self.bids)
                real_price = -bid_price
                trade_qty = min(quantity, bid_order.quantity)
                trades.append(Trade(real_price, trade_qty, bid_order.trader_id, trader_id))
                quantity -= trade_qty
                bid_order.quantity -= trade_qty
                if bid_order.quantity > 0:
                    heapq.heappush(self.bids, (bid_price, bid_ts, bid_order))
            self.trades.extend(trades)
            return trades
        else:
            raise ValueError("Side must be 'buy' or 'sell'")

    def best_bid(self) -> Optional[float]:
        return -self.bids[0][0] if self.bids else None

    def best_ask(self) -> Optional[float]:
        return self.asks[0][0] if self.asks else None

    def spread(self) -> Optional[float]:
        if self.best_bid() is not None and self.best_ask() is not None:
            return self.best_ask() - self.best_bid()
        return None

    def mid_price(self) -> Optional[float]:
        if self.best_bid() is not None and self.best_ask() is not None:
            return (self.best_ask() + self.best_bid()) / 2
        return None

    def depth(self, levels: int = 5) -> Dict:
        # heaps aren't sorted beyond the top, so aggregate resting qty by price
        # then sort - fine for display, don't call this in a hot loop
        bid_levels = {}
        for neg_price, ts, order in self.bids:
            price = -neg_price
            bid_levels[price] = bid_levels.get(price, 0) + order.quantity
        ask_levels = {}
        for price, ts, order in self.asks:
            ask_levels[price] = ask_levels.get(price, 0) + order.quantity

        bids = sorted(bid_levels.items(), key=lambda x: x[0], reverse=True)[:levels]
        asks = sorted(ask_levels.items(), key=lambda x: x[0])[:levels]
        return {'bids': bids, 'asks': asks}

    def print_book(self, levels: int = 5):
        depth_data = self.depth(levels)
        print("=== ORDER BOOK ===")
        for price, qty in depth_data['asks']:
            print(f"ASK  {price:6.2f}  |  {qty}")
        print(f"--- spread: {self.spread():.2f} ---")
        for price, qty in reversed(depth_data['bids']):
            print(f"BID  {price:6.2f}  |  {qty}")
