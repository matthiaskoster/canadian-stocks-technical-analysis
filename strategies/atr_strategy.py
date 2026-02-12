"""ATR Breakout signal strategy."""

import pandas as pd

from config import ATR_BREAKOUT_MULT


def atr_breakout_signals(df: pd.DataFrame, ticker: str) -> list[dict]:
    """ATR breakout: close moves more than 1.5*ATR from previous close."""
    if "atr_14" not in df.columns:
        return []

    signals = []
    prev_close = df["Close"].shift(1)
    prev_atr = df["atr_14"].shift(1)

    # Bullish: close > prev_close + mult * ATR
    bullish = df["Close"] > (prev_close + ATR_BREAKOUT_MULT * prev_atr)
    for date, row in df[bullish].iterrows():
        signals.append({
            "ticker": ticker, "date": date,
            "signal_type": "ATR Breakout Up",
            "direction": "bullish", "price": row["Close"],
            "strategy": "ATR Breakout",
        })

    # Bearish: close < prev_close - mult * ATR
    bearish = df["Close"] < (prev_close - ATR_BREAKOUT_MULT * prev_atr)
    for date, row in df[bearish].iterrows():
        signals.append({
            "ticker": ticker, "date": date,
            "signal_type": "ATR Breakdown",
            "direction": "bearish", "price": row["Close"],
            "strategy": "ATR Breakout",
        })

    return signals
