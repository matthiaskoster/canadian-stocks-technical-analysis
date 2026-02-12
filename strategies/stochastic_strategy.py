"""Stochastic Oscillator signal strategy."""

import pandas as pd

from config import STOCH_OVERSOLD, STOCH_OVERBOUGHT


def stochastic_signals(df: pd.DataFrame, ticker: str) -> list[dict]:
    """%K/%D crossover in oversold/overbought zones."""
    if "stoch_k" not in df.columns or "stoch_d" not in df.columns:
        return []

    signals = []
    prev_k = df["stoch_k"].shift(1)
    prev_d = df["stoch_d"].shift(1)

    # Bullish: %K crosses above %D while both are below oversold level
    bullish = (prev_k <= prev_d) & (df["stoch_k"] > df["stoch_d"]) & (prev_k < STOCH_OVERSOLD)
    for date, row in df[bullish].iterrows():
        signals.append({
            "ticker": ticker, "date": date,
            "signal_type": "Stochastic Bullish Cross",
            "direction": "bullish", "price": row["Close"],
            "strategy": "Stochastic",
        })

    # Bearish: %K crosses below %D while both are above overbought level
    bearish = (prev_k >= prev_d) & (df["stoch_k"] < df["stoch_d"]) & (prev_k > STOCH_OVERBOUGHT)
    for date, row in df[bearish].iterrows():
        signals.append({
            "ticker": ticker, "date": date,
            "signal_type": "Stochastic Bearish Cross",
            "direction": "bearish", "price": row["Close"],
            "strategy": "Stochastic",
        })

    return signals
