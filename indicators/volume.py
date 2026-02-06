"""Volume-based indicators."""

import pandas as pd

from config import VWAP_LOOKBACK


def calculate_vwap(df: pd.DataFrame) -> pd.DataFrame:
    """Calculate rolling 20-day VWAP approximation.

    VWAP = sum(TypicalPrice * Volume) / sum(Volume) over lookback window.
    TypicalPrice = (High + Low + Close) / 3
    """
    typical_price = (df["High"] + df["Low"] + df["Close"]) / 3
    tp_volume = typical_price * df["Volume"]

    df["vwap_20"] = (
        tp_volume.rolling(window=VWAP_LOOKBACK).sum()
        / df["Volume"].rolling(window=VWAP_LOOKBACK).sum()
    )

    return df
