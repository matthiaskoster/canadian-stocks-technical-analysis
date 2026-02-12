"""Technical indicators package."""

import pandas as pd

from indicators.moving_averages import calculate_emas, calculate_smas
from indicators.momentum import calculate_rsi, calculate_macd, calculate_stochastic
from indicators.volume import calculate_vwap, calculate_obv
from indicators.volatility import calculate_atr, calculate_bollinger_bands, calculate_adx


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
    df = calculate_atr(df)
    df = calculate_bollinger_bands(df)
    df = calculate_adx(df)
    df = calculate_obv(df)
    df = calculate_stochastic(df)
    return df
