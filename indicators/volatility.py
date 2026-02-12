"""Volatility and trend-strength indicators: ATR, Bollinger Bands, ADX."""

import pandas as pd

from config import ATR_PERIOD, BB_PERIOD, BB_STD, ADX_PERIOD


def _true_range(df: pd.DataFrame) -> pd.Series:
    """Calculate True Range (shared by ATR and ADX)."""
    high_low = df["High"] - df["Low"]
    high_close = (df["High"] - df["Close"].shift(1)).abs()
    low_close = (df["Low"] - df["Close"].shift(1)).abs()
    return pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)


def calculate_atr(df: pd.DataFrame) -> pd.DataFrame:
    """Average True Range using Wilder's smoothing."""
    tr = _true_range(df)
    df[f"atr_{ATR_PERIOD}"] = tr.ewm(
        alpha=1 / ATR_PERIOD, min_periods=ATR_PERIOD, adjust=False
    ).mean()
    return df


def calculate_bollinger_bands(df: pd.DataFrame) -> pd.DataFrame:
    """Bollinger Bands (middle = SMA, upper/lower = +/- N std devs)."""
    df["bb_middle"] = df["Close"].rolling(window=BB_PERIOD).mean()
    rolling_std = df["Close"].rolling(window=BB_PERIOD).std()
    df["bb_upper"] = df["bb_middle"] + (rolling_std * BB_STD)
    df["bb_lower"] = df["bb_middle"] - (rolling_std * BB_STD)
    df["bb_width"] = (df["bb_upper"] - df["bb_lower"]) / df["bb_middle"]
    return df


def calculate_adx(df: pd.DataFrame) -> pd.DataFrame:
    """Average Directional Index with +DI/-DI using Wilder's smoothing."""
    plus_dm = df["High"].diff()
    minus_dm = -df["Low"].diff()
    plus_dm = plus_dm.where((plus_dm > minus_dm) & (plus_dm > 0), 0.0)
    minus_dm = minus_dm.where((minus_dm > plus_dm) & (minus_dm > 0), 0.0)

    tr = _true_range(df)
    alpha = 1 / ADX_PERIOD
    atr_smooth = tr.ewm(alpha=alpha, min_periods=ADX_PERIOD, adjust=False).mean()

    plus_di = 100 * plus_dm.ewm(alpha=alpha, min_periods=ADX_PERIOD, adjust=False).mean() / atr_smooth
    minus_di = 100 * minus_dm.ewm(alpha=alpha, min_periods=ADX_PERIOD, adjust=False).mean() / atr_smooth

    dx = 100 * (plus_di - minus_di).abs() / (plus_di + minus_di)
    adx = dx.ewm(alpha=alpha, min_periods=ADX_PERIOD * 2, adjust=False).mean()

    df["plus_di"] = plus_di
    df["minus_di"] = minus_di
    df[f"adx_{ADX_PERIOD}"] = adx
    return df
