"""Page 1: Live Signals — Master table of all stocks with current indicators."""

import streamlit as st
import pandas as pd

from data.database import get_latest_prices, get_indicators, get_signals, init_db
from dashboard.components.tables import (
    style_rsi, style_direction, style_macd_status, style_return,
    format_pct, format_price, get_ma_distance, get_macd_status, get_vwap_position,
)
from config import ALL_STOCKS, SECTORS

st.set_page_config(page_title="Live Signals", page_icon="📈", layout="wide")
st.title("Live Signals")

init_db()


@st.cache_data(ttl=300)
def load_overview_data():
    """Load latest prices, indicators, and recent signals."""
    prices = get_latest_prices()
    indicators = get_indicators()
    signals = get_signals(limit=200)
    return prices, indicators, signals


prices, indicators, signals = load_overview_data()

if prices.empty:
    st.warning("No data. Run `python main.py` first.")
    st.stop()

# Build overview table
st.subheader("Stock Overview")

sector_filter = st.multiselect("Filter by sector", ["Banks", "Energy", "Other"], default=["Banks", "Energy", "Other"])

rows = []
for _, price_row in prices.iterrows():
    ticker = price_row["ticker"]
    if SECTORS.get(ticker) not in sector_filter:
        continue

    # Get latest indicators for this ticker
    tk_ind = indicators[indicators["ticker"] == ticker]
    if tk_ind.empty:
        continue
    latest_ind = tk_ind.iloc[-1]

    close = price_row["close"]
    rsi_14 = latest_ind.get("rsi_14")
    macd_val = latest_ind.get("macd")
    macd_sig = latest_ind.get("macd_signal")
    vwap = latest_ind.get("vwap_20")
    ema_50 = latest_ind.get("ema_50")
    ema_200 = latest_ind.get("ema_200")
    sma_200 = latest_ind.get("sma_200")

    rows.append({
        "Ticker": ticker,
        "Name": ALL_STOCKS.get(ticker, ""),
        "Sector": SECTORS.get(ticker, ""),
        "Price": close,
        "Dist EMA50": get_ma_distance(close, ema_50),
        "Dist EMA200": get_ma_distance(close, ema_200),
        "Dist SMA200": get_ma_distance(close, sma_200),
        "RSI(14)": round(rsi_14, 1) if pd.notna(rsi_14) else None,
        "MACD": get_macd_status(macd_val, macd_sig),
        "VWAP": get_vwap_position(close, vwap),
    })

overview_df = pd.DataFrame(rows)

if not overview_df.empty:
    styled = overview_df.style.applymap(style_rsi, subset=["RSI(14)"])
    styled = styled.applymap(style_macd_status, subset=["MACD"])
    styled = styled.format({"Price": "${:.2f}"}, na_rep="—")
    st.dataframe(styled, use_container_width=True, hide_index=True, height=700)
else:
    st.info("No stocks match the selected sectors.")

# Recent signals
st.subheader("Recent Signals")

if not signals.empty:
    sig_display = signals[["date", "ticker", "signal_type", "direction", "price", "strategy"]].copy()
    sig_display["date"] = sig_display["date"].dt.strftime("%Y-%m-%d")
    sig_display.columns = ["Date", "Ticker", "Signal", "Direction", "Price", "Strategy"]

    styled_sig = sig_display.head(50).style.applymap(style_direction, subset=["Direction"])
    styled_sig = styled_sig.format({"Price": "${:.2f}"}, na_rep="—")
    st.dataframe(styled_sig, use_container_width=True, hide_index=True)
else:
    st.info("No signals detected yet.")
