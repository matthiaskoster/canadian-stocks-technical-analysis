"""Signal detection strategies package."""

import pandas as pd

from strategies.ma_crossover import (
    golden_death_cross,
    ema_10_50_crossover,
    ema_5_20_crossover,
    vwap_crossover,
)
from strategies.rsi_strategy import (
    rsi_oversold_overbought,
    rsi_midline_cross,
    macd_crossover,
)
from strategies.combined_signals import combined_momentum


def detect_all_signals(df: pd.DataFrame, ticker: str) -> list[dict]:
    """Run all signal detection strategies on indicator-enriched DataFrame."""
    all_signals = []
    all_signals.extend(golden_death_cross(df, ticker))
    all_signals.extend(ema_10_50_crossover(df, ticker))
    all_signals.extend(ema_5_20_crossover(df, ticker))
    all_signals.extend(vwap_crossover(df, ticker))
    all_signals.extend(rsi_oversold_overbought(df, ticker))
    all_signals.extend(rsi_midline_cross(df, ticker))
    all_signals.extend(macd_crossover(df, ticker))
    all_signals.extend(combined_momentum(df, ticker))
    return all_signals


# Strategy definitions for backtesting: maps strategy name to (entry_func, exit_func)
# Each func takes DataFrame and returns boolean Series for entry/exit days.

def _ema_10_50_entry(df: pd.DataFrame) -> pd.Series:
    prev = df["ema_10"].shift(1)
    prev_slow = df["ema_50"].shift(1)
    return (prev <= prev_slow) & (df["ema_10"] > df["ema_50"])


def _ema_10_50_exit(df: pd.DataFrame) -> pd.Series:
    prev = df["ema_10"].shift(1)
    prev_slow = df["ema_50"].shift(1)
    return (prev >= prev_slow) & (df["ema_10"] < df["ema_50"])


def _ema_5_20_entry(df: pd.DataFrame) -> pd.Series:
    prev = df["ema_5"].shift(1)
    prev_slow = df["ema_20"].shift(1)
    return (prev <= prev_slow) & (df["ema_5"] > df["ema_20"])


def _ema_5_20_exit(df: pd.DataFrame) -> pd.Series:
    prev = df["ema_5"].shift(1)
    prev_slow = df["ema_20"].shift(1)
    return (prev >= prev_slow) & (df["ema_5"] < df["ema_20"])


def _rsi_entry(df: pd.DataFrame) -> pd.Series:
    prev = df["rsi_14"].shift(1)
    return (prev <= 30) & (df["rsi_14"] > 30)


def _rsi_exit(df: pd.DataFrame) -> pd.Series:
    prev = df["rsi_14"].shift(1)
    return (prev >= 70) & (df["rsi_14"] < 70)


def _macd_entry(df: pd.DataFrame) -> pd.Series:
    prev_macd = df["macd"].shift(1)
    prev_sig = df["macd_signal"].shift(1)
    return (prev_macd <= prev_sig) & (df["macd"] > df["macd_signal"])


def _macd_exit(df: pd.DataFrame) -> pd.Series:
    prev_macd = df["macd"].shift(1)
    prev_sig = df["macd_signal"].shift(1)
    return (prev_macd >= prev_sig) & (df["macd"] < df["macd_signal"])


def _vwap_entry(df: pd.DataFrame) -> pd.Series:
    prev_close = df["Close"].shift(1)
    prev_vwap = df["vwap_20"].shift(1)
    return (prev_close <= prev_vwap) & (df["Close"] > df["vwap_20"])


def _vwap_exit(df: pd.DataFrame) -> pd.Series:
    prev_close = df["Close"].shift(1)
    prev_vwap = df["vwap_20"].shift(1)
    return (prev_close >= prev_vwap) & (df["Close"] < df["vwap_20"])


def _combined_entry(df: pd.DataFrame) -> pd.Series:
    cond = (
        (df["ema_10"] > df["ema_50"])
        & (df["rsi_14"] > 50) & (df["rsi_14"] < 70)
        & (df["macd_histogram"] > 0)
        & (df["Close"] > df["vwap_20"])
    )
    return cond & ~cond.shift(1, fill_value=False)


def _combined_exit(df: pd.DataFrame) -> pd.Series:
    cond = (
        (df["ema_10"] < df["ema_50"])
        & (df["rsi_14"] < 50) & (df["rsi_14"] > 30)
        & (df["macd_histogram"] < 0)
        & (df["Close"] < df["vwap_20"])
    )
    return cond & ~cond.shift(1, fill_value=False)


BACKTEST_STRATEGIES = {
    "EMA 10/50": (_ema_10_50_entry, _ema_10_50_exit),
    "EMA 5/20": (_ema_5_20_entry, _ema_5_20_exit),
    "RSI": (_rsi_entry, _rsi_exit),
    "MACD": (_macd_entry, _macd_exit),
    "VWAP": (_vwap_entry, _vwap_exit),
    "Combined": (_combined_entry, _combined_exit),
}
