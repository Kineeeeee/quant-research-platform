import os
from pathlib import Path

# Project root directory
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent

# Data directories
DATA_DIR = PROJECT_ROOT / "data"
RAW_DATA_DIR = DATA_DIR / "raw"
PROCESSED_DATA_DIR = DATA_DIR / "processed"

# Default settings
DEFAULT_START_DATE = "2010-01-01"
DEFAULT_END_DATE = "2023-12-31"

def ensure_directories():
    """Ensure that necessary data directories exist."""
    RAW_DATA_DIR.mkdir(parents=True, exist_ok=True)
    PROCESSED_DATA_DIR.mkdir(parents=True, exist_ok=True)

# Run this on import to ensure directories are ready
ensure_directories()
