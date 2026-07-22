
import pandas as pd
import logging
from src.utils.config import RAW_DATA_DIR, PROCESSED_DATA_DIR

logger = logging.getLogger(__name__)

class DataCleaner:
    """
    Handles cleaning and preprocessing of raw market data.
    """
    
    @staticmethod
    def clean_data(ticker: str) -> pd.DataFrame:
        """
        Loads raw data for a ticker, cleans it, and returns the processed DataFrame.
        """
        raw_file_path = RAW_DATA_DIR / f"{ticker}_raw.csv"
        
        if not raw_file_path.exists():
            logger.error("Raw file does not exist!")
            return pd.DataFrame()
            
        # Read CSV, sort by date, and forward/back-fill missing values
        df = pd.read_csv(raw_file_path, index_col='Date', parse_dates=True)
        df = df.sort_index()
        df = df.ffill().bfill().dropna(how='all') 
        
        
        return df

    @staticmethod
    def save_processed_data(data: pd.DataFrame, ticker: str) -> str:
        """
        Saves cleaned data to the processed data directory as a CSV file.
        """

        if data.empty:
            return ""
        file_path = PROCESSED_DATA_DIR / f"{ticker}_processed.csv"
        data.to_csv(file_path)
        
        return str(file_path)
