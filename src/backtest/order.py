from enum import Enum
from dataclasses import dataclass
from typing import Optional
from datetime import datetime

class OrderType(Enum):
    MARKET = 'MARKET'
    LIMIT = 'LIMIT'
    STOP = 'STOP'

class OrderDirection(Enum):
    BUY = 'BUY'
    SELL = 'SELL'

class OrderStatus(Enum):
    PENDING = 'PENDING'
    FILLED = 'FILLED'
    CANCELLED = 'CANCELLED'
    REJECTED = 'REJECTED'

@dataclass
class Order:
    ticker: str
    direction: OrderDirection
    quantity: float
    order_type: OrderType
    price: Optional[float] = None  # Needed for Limit/Stop orders
    status: OrderStatus = OrderStatus.PENDING
    created_at: Optional[datetime] = None
    filled_at: Optional[datetime] = None
    filled_price: Optional[float] = None
    stop_loss_price: Optional[float] = None
    take_profit_price: Optional[float] = None