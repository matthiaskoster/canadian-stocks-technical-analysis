"""Combined multi-indicator signal strategies."""

import pandas as pd

from config import RSI_OVERSOLD, RSI_OVERBOUGHT


def combined_momentum(df: pd.DataFrame, ticker: str) -> list[dict]:
    """Combined signal: requires alignment of multiple indicators.

    Bullish: EMA 10 > EMA 50, RSI(14) > 50 but < 70, MACD histogram > 0, price > VWAP.
    Bearish: EMA 10 < EMA 50, RSI(14) < 50 but > 30, MACD histogram < 0, price < VWAP.

    Only triggers on the transition day (when all conditions first align).
    """
    required = ["ema_10", "ema_50", "rsi_14", "macd_histogram", "vwap_20"]
    if not all(col in df.columns for col in required):
        return []

    signals = []

    bullish_cond = (
        (df["ema_10"] > df["ema_50"])
        & (df["rsi_14"] > 50)
        & (df["rsi_14"] < RSI_OVERBOUGHT)
        & (df["macd_histogram"] > 0)
        & (df["Close"] > df["vwap_20"])
    )

    bearish_cond = (
        (df["ema_10"] < df["ema_50"])
        & (df["rsi_14"] < 50)
        & (df["rsi_14"] > RSI_OVERSOLD)
        & (df["macd_histogram"] < 0)
        & (df["Close"] < df["vwap_20"])
    )

    # Only trigger on transition (previous day was NOT aligned)
    bull_transition = bullish_cond & ~bullish_cond.shift(1, fill_value=False)
    bear_transition = bearish_cond & ~bearish_cond.shift(1, fill_value=False)

    for date, row in df[bull_transition].iterrows():
        signals.append({
            "ticker": ticker, "date": date, "signal_type": "Combined Momentum Bullish",
            "direction": "bullish", "price": row["Close"], "strategy": "Combined",
        })

    for date, row in df[bear_transition].iterrows():
        signals.append({
            "ticker": ticker, "date": date, "signal_type": "Combined Momentum Bearish",
            "direction": "bearish", "price": row["Close"], "strategy": "Combined",
        })

    return signals
