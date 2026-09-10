# WIP - started this to extend DataLoader to baskets (equities + crypto) for
# the portfolio side, but ran out of summer. Signatures are stubbed; the
# portfolio code currently just pulls prices via yfinance directly. Come back
# to this if the multi-asset work gets serious.
import pandas as pd
import numpy as np
from typing import List, Dict, Optional
from src.data.loader import DataLoader
from src.data.cleaner import DataCleaner


class MultiAssetManager:
    """Planned: fetch + align multiple tickers (incl. crypto) into one price panel. Not finished."""

    def __init__(self, tickers: List[str], start_date: str, end_date: str):
        self.tickers = tickers
        self.start_date = start_date
        self.end_date = end_date
        self.data: Dict[str, pd.DataFrame] = {}

    def fetch_all(self) -> Dict[str, pd.DataFrame]:
        raise NotImplementedError

    def get_close_prices(self) -> pd.DataFrame:
        raise NotImplementedError

    def calculate_correlation(self, period: int = 252) -> pd.DataFrame:
        raise NotImplementedError

    def calculate_returns_table(self) -> pd.DataFrame:
        raise NotImplementedError
