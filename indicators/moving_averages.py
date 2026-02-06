"""Exponential and Simple Moving Averages."""

import pandas as pd

from config import EMA_PERIODS, SMA_PERIODS


def calculate_emas(df: pd.DataFrame) -> pd.DataFrame:
    """Calculate EMAs for all configured periods. Expects 'Close' column."""
    for period in EMA_PERIODS:
        df[f"ema_{period}"] = df["Close"].ewm(span=period, adjust=False).mean()
    return df


def calculate_smas(df: pd.DataFrame) -> pd.DataFrame:
    """Calculate SMAs for all configured periods."""
    for period in SMA_PERIODS:
        df[f"sma_{period}"] = df["Close"].rolling(window=period).mean()
    return df
