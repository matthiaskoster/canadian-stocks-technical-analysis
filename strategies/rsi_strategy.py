"""RSI-based signal strategies."""

import pandas as pd

from config import RSI_OVERSOLD, RSI_OVERBOUGHT, RSI_MIDLINE


def rsi_oversold_overbought(df: pd.DataFrame, ticker: str) -> list[dict]:
    """RSI(14) crossing out of oversold/overbought zones."""
    if "rsi_14" not in df.columns:
        return []

    signals = []
    rsi = df["rsi_14"]
    prev_rsi = rsi.shift(1)

    # Bullish: RSI crosses above oversold level (coming out of oversold)
    bullish = (prev_rsi <= RSI_OVERSOLD) & (rsi > RSI_OVERSOLD)
    for date, row in df[bullish].iterrows():
        signals.append({
            "ticker": ticker, "date": date, "signal_type": "RSI Oversold Recovery",
            "direction": "bullish", "price": row["Close"], "strategy": "RSI",
        })

    # Bearish: RSI crosses below overbought level (coming out of overbought)
    bearish = (prev_rsi >= RSI_OVERBOUGHT) & (rsi < RSI_OVERBOUGHT)
    for date, row in df[bearish].iterrows():
        signals.append({
            "ticker": ticker, "date": date, "signal_type": "RSI Overbought Reversal",
            "direction": "bearish", "price": row["Close"], "strategy": "RSI",
        })

    return signals


def rsi_midline_cross(df: pd.DataFrame, ticker: str) -> list[dict]:
    """RSI(21) crossing the 50 midline."""
    if "rsi_21" not in df.columns:
        return []

    signals = []
    rsi = df["rsi_21"]
    prev_rsi = rsi.shift(1)

    bullish = (prev_rsi <= RSI_MIDLINE) & (rsi > RSI_MIDLINE)
    for date, row in df[bullish].iterrows():
        signals.append({
            "ticker": ticker, "date": date, "signal_type": "RSI Midline Bullish",
            "direction": "bullish", "price": row["Close"], "strategy": "RSI",
        })

    bearish = (prev_rsi >= RSI_MIDLINE) & (rsi < RSI_MIDLINE)
    for date, row in df[bearish].iterrows():
        signals.append({
            "ticker": ticker, "date": date, "signal_type": "RSI Midline Bearish",
            "direction": "bearish", "price": row["Close"], "strategy": "RSI",
        })

    return signals


def macd_crossover(df: pd.DataFrame, ticker: str) -> list[dict]:
    """MACD line crossing signal line."""
    if "macd" not in df.columns or "macd_signal" not in df.columns:
        return []

    signals = []
    prev_macd = df["macd"].shift(1)
    prev_signal = df["macd_signal"].shift(1)

    bullish = (prev_macd <= prev_signal) & (df["macd"] > df["macd_signal"])
    for date, row in df[bullish].iterrows():
        signals.append({
            "ticker": ticker, "date": date, "signal_type": "MACD Bullish Cross",
            "direction": "bullish", "price": row["Close"], "strategy": "MACD",
        })

    bearish = (prev_macd >= prev_signal) & (df["macd"] < df["macd_signal"])
    for date, row in df[bearish].iterrows():
        signals.append({
            "ticker": ticker, "date": date, "signal_type": "MACD Bearish Cross",
            "direction": "bearish", "price": row["Close"], "strategy": "MACD",
        })

    return signals
