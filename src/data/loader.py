import yfinance as yf
import pandas as pd
import logging
from src.utils.config import RAW_DATA_DIR

logger = logging.getLogger(__name__)

class DataLoader:
    """
    Handles downloading market data from Yahoo Finance.
    """
    
    @staticmethod
    def fetch_historical_data(ticker: str, start_date: str, end_date: str) -> pd.DataFrame:
        """
        Fetches historical daily data for a given ticker and date range.
        
        Args:
            ticker (str): The stock symbol (e.g., 'AAPL', 'BTC-USD').
            start_date (str): Start date in YYYY-MM-DD format.
            end_date (str): End date in YYYY-MM-DD format.
            
        Returns:
            pd.DataFrame: DataFrame containing Date, Open, High, Low, Close, Adj Close, Volume.
        """
        logger.info(f"Downloading data for {ticker}...")
        
        data = yf.download(ticker, start=start_date, end=end_date)
        
        # Fix for newer yfinance versions returning MultiIndex columns
        if isinstance(data.columns, pd.MultiIndex):
            data.columns = data.columns.droplevel(1)
            
        return data

    @staticmethod
    def save_raw_data(data: pd.DataFrame, ticker: str) -> str:
        """
        Saves a DataFrame to the raw data directory as a CSV file.
        """
        if data.empty:
            return ""
            
        file_path = RAW_DATA_DIR / f"{ticker}_raw.csv"
        data.to_csv(file_path)
        
        return str(file_path)
