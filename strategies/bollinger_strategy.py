"""Bollinger Bands signal strategy."""

import pandas as pd


def bollinger_signals(df: pd.DataFrame, ticker: str) -> list[dict]:
    """Price recovering above lower band (bullish) / falling below upper band (bearish)."""
    if "bb_lower" not in df.columns or "bb_upper" not in df.columns:
        return []

    signals = []
    prev_close = df["Close"].shift(1)
    prev_lower = df["bb_lower"].shift(1)
    prev_upper = df["bb_upper"].shift(1)

    # Bullish: price was below lower band, now recovers above it
    bullish = (prev_close <= prev_lower) & (df["Close"] > df["bb_lower"])
    for date, row in df[bullish].iterrows():
        signals.append({
            "ticker": ticker, "date": date,
            "signal_type": "BB Lower Band Recovery",
            "direction": "bullish", "price": row["Close"],
            "strategy": "Bollinger Bands",
        })

    # Bearish: price was above upper band, now falls below it
    bearish = (prev_close >= prev_upper) & (df["Close"] < df["bb_upper"])
    for date, row in df[bearish].iterrows():
        signals.append({
            "ticker": ticker, "date": date,
            "signal_type": "BB Upper Band Rejection",
            "direction": "bearish", "price": row["Close"],
            "strategy": "Bollinger Bands",
        })

    return signals
