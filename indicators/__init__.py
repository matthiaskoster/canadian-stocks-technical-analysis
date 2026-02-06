"""Technical indicators package."""

import pandas as pd

from indicators.moving_averages import calculate_emas, calculate_smas
from indicators.momentum import calculate_rsi, calculate_macd
from indicators.volume import calculate_vwap


def calculate_all_indicators(df: pd.DataFrame) -> pd.DataFrame:
    """Calculate all technical indicators on a price DataFrame.

    Expects columns: Open, High, Low, Close, Volume with DatetimeIndex.
    Returns the same DataFrame with indicator columns added.
    """
    df = df.copy()
    df = calculate_emas(df)
    df = calculate_smas(df)
    df = calculate_rsi(df)
    df = calculate_macd(df)
    df = calculate_vwap(df)
    return df
