"""ADX DI Crossover signal strategy."""

import pandas as pd

from config import ADX_TREND_THRESHOLD


def adx_di_cross_signals(df: pd.DataFrame, ticker: str) -> list[dict]:
    """+DI/-DI crossover filtered by ADX > threshold."""
    if "adx_14" not in df.columns or "plus_di" not in df.columns or "minus_di" not in df.columns:
        return []

    signals = []
    prev_plus = df["plus_di"].shift(1)
    prev_minus = df["minus_di"].shift(1)
    strong_trend = df["adx_14"] > ADX_TREND_THRESHOLD

    # Bullish: +DI crosses above -DI with ADX > 20
    bullish = (prev_plus <= prev_minus) & (df["plus_di"] > df["minus_di"]) & strong_trend
    for date, row in df[bullish].iterrows():
        signals.append({
            "ticker": ticker, "date": date,
            "signal_type": "ADX +DI Bullish Cross",
            "direction": "bullish", "price": row["Close"],
            "strategy": "ADX DI Cross",
        })

    # Bearish: -DI crosses above +DI with ADX > 20
    bearish = (prev_minus <= prev_plus) & (df["minus_di"] > df["plus_di"]) & strong_trend
    for date, row in df[bearish].iterrows():
        signals.append({
            "ticker": ticker, "date": date,
            "signal_type": "ADX -DI Bearish Cross",
            "direction": "bearish", "price": row["Close"],
            "strategy": "ADX DI Cross",
        })

    return signals
