"""Signal detection strategies package."""

import pandas as pd

from config import (
    ATR_BREAKOUT_MULT, ADX_TREND_THRESHOLD, OBV_EMA_PERIOD,
    STOCH_OVERSOLD, STOCH_OVERBOUGHT,
)
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
from strategies.bollinger_strategy import bollinger_signals
from strategies.atr_strategy import atr_breakout_signals
from strategies.adx_strategy import adx_di_cross_signals
from strategies.obv_strategy import obv_trend_signals
from strategies.stochastic_strategy import stochastic_signals


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
    all_signals.extend(bollinger_signals(df, ticker))
    all_signals.extend(atr_breakout_signals(df, ticker))
    all_signals.extend(adx_di_cross_signals(df, ticker))
    all_signals.extend(obv_trend_signals(df, ticker))
    all_signals.extend(stochastic_signals(df, ticker))
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


# --- New strategy entry/exit functions ---

def _bb_entry(df: pd.DataFrame) -> pd.Series:
    prev_close = df["Close"].shift(1)
    prev_lower = df["bb_lower"].shift(1)
    return (prev_close <= prev_lower) & (df["Close"] > df["bb_lower"])


def _bb_exit(df: pd.DataFrame) -> pd.Series:
    prev_close = df["Close"].shift(1)
    prev_upper = df["bb_upper"].shift(1)
    return (prev_close >= prev_upper) & (df["Close"] < df["bb_upper"])


def _atr_entry(df: pd.DataFrame) -> pd.Series:
    prev_close = df["Close"].shift(1)
    prev_atr = df["atr_14"].shift(1)
    return df["Close"] > (prev_close + ATR_BREAKOUT_MULT * prev_atr)


def _atr_exit(df: pd.DataFrame) -> pd.Series:
    prev_close = df["Close"].shift(1)
    prev_atr = df["atr_14"].shift(1)
    return df["Close"] < (prev_close - ATR_BREAKOUT_MULT * prev_atr)


def _adx_entry(df: pd.DataFrame) -> pd.Series:
    prev_plus = df["plus_di"].shift(1)
    prev_minus = df["minus_di"].shift(1)
    return ((prev_plus <= prev_minus) & (df["plus_di"] > df["minus_di"])
            & (df["adx_14"] > ADX_TREND_THRESHOLD))


def _adx_exit(df: pd.DataFrame) -> pd.Series:
    prev_plus = df["plus_di"].shift(1)
    prev_minus = df["minus_di"].shift(1)
    return ((prev_minus <= prev_plus) & (df["minus_di"] > df["plus_di"])
            & (df["adx_14"] > ADX_TREND_THRESHOLD))


def _obv_entry(df: pd.DataFrame) -> pd.Series:
    obv_ema = df["obv"].ewm(span=OBV_EMA_PERIOD, adjust=False).mean()
    prev_obv = df["obv"].shift(1)
    prev_ema = obv_ema.shift(1)
    return (prev_obv <= prev_ema) & (df["obv"] > obv_ema)


def _obv_exit(df: pd.DataFrame) -> pd.Series:
    obv_ema = df["obv"].ewm(span=OBV_EMA_PERIOD, adjust=False).mean()
    prev_obv = df["obv"].shift(1)
    prev_ema = obv_ema.shift(1)
    return (prev_obv >= prev_ema) & (df["obv"] < obv_ema)


def _stoch_entry(df: pd.DataFrame) -> pd.Series:
    prev_k = df["stoch_k"].shift(1)
    prev_d = df["stoch_d"].shift(1)
    return (prev_k <= prev_d) & (df["stoch_k"] > df["stoch_d"]) & (prev_k < STOCH_OVERSOLD)


def _stoch_exit(df: pd.DataFrame) -> pd.Series:
    prev_k = df["stoch_k"].shift(1)
    prev_d = df["stoch_d"].shift(1)
    return (prev_k >= prev_d) & (df["stoch_k"] < df["stoch_d"]) & (prev_k > STOCH_OVERBOUGHT)


BACKTEST_STRATEGIES = {
    "EMA 10/50": (_ema_10_50_entry, _ema_10_50_exit),
    "EMA 5/20": (_ema_5_20_entry, _ema_5_20_exit),
    "RSI": (_rsi_entry, _rsi_exit),
    "MACD": (_macd_entry, _macd_exit),
    "VWAP": (_vwap_entry, _vwap_exit),
    "Combined": (_combined_entry, _combined_exit),
    "Bollinger Bands": (_bb_entry, _bb_exit),
    "ATR Breakout": (_atr_entry, _atr_exit),
    "ADX DI Cross": (_adx_entry, _adx_exit),
    "OBV Trend": (_obv_entry, _obv_exit),
    "Stochastic": (_stoch_entry, _stoch_exit),
}
