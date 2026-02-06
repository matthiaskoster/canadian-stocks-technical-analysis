"""Moving average crossover signal strategies."""

import pandas as pd


def _crossover(fast: pd.Series, slow: pd.Series) -> tuple[pd.Series, pd.Series]:
    """Detect crossover points. Returns (bullish_cross, bearish_cross) boolean Series."""
    prev_fast = fast.shift(1)
    prev_slow = slow.shift(1)
    bullish = (prev_fast <= prev_slow) & (fast > slow)
    bearish = (prev_fast >= prev_slow) & (fast < slow)
    return bullish, bearish


def golden_death_cross(df: pd.DataFrame, ticker: str) -> list[dict]:
    """SMA 50/200 Golden Cross (bullish) and Death Cross (bearish).

    Pullback filter: only trigger if price is within 3% of the SMA 50.
    """
    if "sma_50" not in df.columns or "sma_200" not in df.columns:
        return []

    signals = []
    bullish, bearish = _crossover(df["sma_50"], df["sma_200"])

    for date, row in df[bullish].iterrows():
        # Pullback filter: price within 3% of SMA 50
        if abs(row["Close"] - row["sma_50"]) / row["sma_50"] <= 0.03:
            signals.append({
                "ticker": ticker, "date": date, "signal_type": "Golden Cross",
                "direction": "bullish", "price": row["Close"], "strategy": "MA Crossover",
            })

    for date, row in df[bearish].iterrows():
        if abs(row["Close"] - row["sma_50"]) / row["sma_50"] <= 0.03:
            signals.append({
                "ticker": ticker, "date": date, "signal_type": "Death Cross",
                "direction": "bearish", "price": row["Close"], "strategy": "MA Crossover",
            })

    return signals


def ema_10_50_crossover(df: pd.DataFrame, ticker: str) -> list[dict]:
    """EMA 10/50 crossover signals."""
    if "ema_10" not in df.columns or "ema_50" not in df.columns:
        return []

    signals = []
    bullish, bearish = _crossover(df["ema_10"], df["ema_50"])

    for date, row in df[bullish].iterrows():
        signals.append({
            "ticker": ticker, "date": date, "signal_type": "EMA 10/50 Bullish Cross",
            "direction": "bullish", "price": row["Close"], "strategy": "MA Crossover",
        })
    for date, row in df[bearish].iterrows():
        signals.append({
            "ticker": ticker, "date": date, "signal_type": "EMA 10/50 Bearish Cross",
            "direction": "bearish", "price": row["Close"], "strategy": "MA Crossover",
        })

    return signals


def ema_5_20_crossover(df: pd.DataFrame, ticker: str) -> list[dict]:
    """EMA 5/20 crossover signals (shorter-term)."""
    if "ema_5" not in df.columns or "ema_20" not in df.columns:
        return []

    signals = []
    bullish, bearish = _crossover(df["ema_5"], df["ema_20"])

    for date, row in df[bullish].iterrows():
        signals.append({
            "ticker": ticker, "date": date, "signal_type": "EMA 5/20 Bullish Cross",
            "direction": "bullish", "price": row["Close"], "strategy": "MA Crossover",
        })
    for date, row in df[bearish].iterrows():
        signals.append({
            "ticker": ticker, "date": date, "signal_type": "EMA 5/20 Bearish Cross",
            "direction": "bearish", "price": row["Close"], "strategy": "MA Crossover",
        })

    return signals


def vwap_crossover(df: pd.DataFrame, ticker: str) -> list[dict]:
    """Price crossing above/below VWAP signals."""
    if "vwap_20" not in df.columns:
        return []

    signals = []
    bullish, bearish = _crossover(df["Close"], df["vwap_20"])

    for date, row in df[bullish].iterrows():
        signals.append({
            "ticker": ticker, "date": date, "signal_type": "VWAP Bullish Cross",
            "direction": "bullish", "price": row["Close"], "strategy": "VWAP",
        })
    for date, row in df[bearish].iterrows():
        signals.append({
            "ticker": ticker, "date": date, "signal_type": "VWAP Bearish Cross",
            "direction": "bearish", "price": row["Close"], "strategy": "VWAP",
        })

    return signals
