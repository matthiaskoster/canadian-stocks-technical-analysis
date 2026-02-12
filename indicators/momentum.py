"""RSI and MACD indicators."""

import pandas as pd

from config import RSI_PERIODS, MACD_FAST, MACD_SLOW, MACD_SIGNAL, STOCH_K_PERIOD, STOCH_D_PERIOD


def calculate_rsi(df: pd.DataFrame) -> pd.DataFrame:
    """Calculate RSI using Wilder's smoothing method (ewm with alpha=1/period)."""
    for period in RSI_PERIODS:
        delta = df["Close"].diff()
        gain = delta.where(delta > 0, 0.0)
        loss = (-delta).where(delta < 0, 0.0)

        # Wilder's smoothing: equivalent to ewm(alpha=1/period)
        avg_gain = gain.ewm(alpha=1 / period, min_periods=period, adjust=False).mean()
        avg_loss = loss.ewm(alpha=1 / period, min_periods=period, adjust=False).mean()

        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))

        # Handle division by zero (all gains, no losses)
        rsi = rsi.where(avg_loss != 0, 100.0)
        df[f"rsi_{period}"] = rsi

    return df


def calculate_macd(df: pd.DataFrame) -> pd.DataFrame:
    """Calculate MACD line, signal line, and histogram."""
    ema_fast = df["Close"].ewm(span=MACD_FAST, adjust=False).mean()
    ema_slow = df["Close"].ewm(span=MACD_SLOW, adjust=False).mean()

    df["macd"] = ema_fast - ema_slow
    df["macd_signal"] = df["macd"].ewm(span=MACD_SIGNAL, adjust=False).mean()
    df["macd_histogram"] = df["macd"] - df["macd_signal"]

    return df


def calculate_stochastic(df: pd.DataFrame) -> pd.DataFrame:
    """Stochastic Oscillator %K and %D."""
    low_min = df["Low"].rolling(window=STOCH_K_PERIOD).min()
    high_max = df["High"].rolling(window=STOCH_K_PERIOD).max()
    df["stoch_k"] = 100 * (df["Close"] - low_min) / (high_max - low_min)
    df["stoch_d"] = df["stoch_k"].rolling(window=STOCH_D_PERIOD).mean()
    return df
