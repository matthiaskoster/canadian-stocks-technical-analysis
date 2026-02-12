"""OBV Trend signal strategy."""

import pandas as pd

from config import OBV_EMA_PERIOD


def obv_trend_signals(df: pd.DataFrame, ticker: str) -> list[dict]:
    """OBV crossing its 20-period EMA."""
    if "obv" not in df.columns:
        return []

    signals = []
    obv_ema = df["obv"].ewm(span=OBV_EMA_PERIOD, adjust=False).mean()
    prev_obv = df["obv"].shift(1)
    prev_ema = obv_ema.shift(1)

    # Bullish: OBV crosses above its EMA
    bullish = (prev_obv <= prev_ema) & (df["obv"] > obv_ema)
    for date, row in df[bullish].iterrows():
        signals.append({
            "ticker": ticker, "date": date,
            "signal_type": "OBV Bullish Cross",
            "direction": "bullish", "price": row["Close"],
            "strategy": "OBV Trend",
        })

    # Bearish: OBV crosses below its EMA
    bearish = (prev_obv >= prev_ema) & (df["obv"] < obv_ema)
    for date, row in df[bearish].iterrows():
        signals.append({
            "ticker": ticker, "date": date,
            "signal_type": "OBV Bearish Cross",
            "direction": "bearish", "price": row["Close"],
            "strategy": "OBV Trend",
        })

    return signals
