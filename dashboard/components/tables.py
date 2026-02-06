"""Table styling helpers for the Streamlit dashboard."""

import pandas as pd


def style_rsi(val) -> str:
    """Color-code RSI values: green < 30, red > 70, neutral otherwise."""
    if pd.isna(val):
        return ""
    if val < 30:
        return "color: #26a69a; font-weight: bold"
    elif val > 70:
        return "color: #ef5350; font-weight: bold"
    return ""


def style_direction(val) -> str:
    """Color-code bullish/bearish direction."""
    if val == "bullish":
        return "color: #26a69a; font-weight: bold"
    elif val == "bearish":
        return "color: #ef5350; font-weight: bold"
    return ""


def style_return(val) -> str:
    """Color-code return percentages."""
    if pd.isna(val):
        return ""
    if val > 0:
        return "color: #26a69a"
    elif val < 0:
        return "color: #ef5350"
    return ""


def style_macd_status(val) -> str:
    """Color-code MACD status text."""
    if "Bullish" in str(val):
        return "color: #26a69a"
    elif "Bearish" in str(val):
        return "color: #ef5350"
    return ""


def format_pct(val) -> str:
    """Format a value as percentage string."""
    if pd.isna(val):
        return "—"
    return f"{val:+.2f}%"


def format_price(val) -> str:
    """Format a value as dollar price."""
    if pd.isna(val):
        return "—"
    return f"${val:.2f}"


def get_ma_distance(close: float, ma_val: float) -> str:
    """Format distance from a moving average as percentage."""
    if pd.isna(ma_val) or pd.isna(close) or ma_val == 0:
        return "—"
    pct = (close - ma_val) / ma_val * 100
    return f"{pct:+.1f}%"


def get_macd_status(macd: float, signal: float) -> str:
    """Return MACD status string."""
    if pd.isna(macd) or pd.isna(signal):
        return "—"
    if macd > signal:
        return "Bullish"
    return "Bearish"


def get_vwap_position(close: float, vwap: float) -> str:
    """Return position relative to VWAP."""
    if pd.isna(vwap) or pd.isna(close):
        return "—"
    return "Above" if close > vwap else "Below"
