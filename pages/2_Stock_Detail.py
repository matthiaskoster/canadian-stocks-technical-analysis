"""Page 2: Stock Detail — Individual stock deep dive with interactive charts."""

import streamlit as st
import pandas as pd

from data.database import get_prices, get_indicators, get_signals, init_db
from dashboard.components.charts import (
    create_candlestick_chart, create_rsi_chart, create_macd_chart,
)
from dashboard.components.styles import apply_custom_css
from config import ALL_STOCKS

st.set_page_config(page_title="Stock Detail", page_icon="📈", layout="wide")
apply_custom_css()
st.title("Stock Detail")

init_db()

ticker_options = list(ALL_STOCKS.keys())
ticker_labels = {t: f"{t} — {ALL_STOCKS[t]}" for t in ticker_options}

selected = st.selectbox("Select Stock", ticker_options, format_func=lambda t: ticker_labels[t])


@st.cache_data(ttl=300)
def load_stock_data(ticker):
    prices = get_prices(ticker)
    ind = get_indicators(ticker)
    sigs = get_signals(ticker)
    return prices, ind, sigs


prices, indicators, signals = load_stock_data(selected)

if prices.empty:
    st.warning(f"No data for {selected}. Run `python main.py --ticker {selected}` first.")
    st.stop()

# Time range filter
st.subheader(f"{ALL_STOCKS[selected]} ({selected})")

time_range = st.radio(
    "Time Range", ["3M", "6M", "1Y", "All"], horizontal=True, index=2,
)

cutoff_map = {"3M": 63, "6M": 126, "1Y": 252, "All": len(prices)}
n_days = cutoff_map[time_range]

prices_view = prices.tail(n_days)
ind_view = indicators[indicators["date"].isin(prices_view["date"])] if not indicators.empty else indicators
sig_view = signals[signals["date"].isin(prices_view["date"])] if not signals.empty else signals

# Candlestick chart with overlays
col_ema, col_sma, col_vwap, col_bb = st.columns(4)
show_emas = col_ema.checkbox("Show EMAs", value=True)
show_smas = col_sma.checkbox("Show SMAs", value=True)
show_vwap = col_vwap.checkbox("Show VWAP", value=True)
show_bb = col_bb.checkbox("Show Bollinger Bands", value=False)

fig_candle = create_candlestick_chart(
    prices_view, ind_view, sig_view,
    title=f"{selected} Price Chart",
    show_emas=show_emas, show_smas=show_smas, show_vwap=show_vwap,
    show_bb=show_bb,
    height=500,
)
st.plotly_chart(fig_candle, use_container_width=True)

# RSI and MACD subplots
col1, col2 = st.columns(2)

with col1:
    if not ind_view.empty:
        fig_rsi = create_rsi_chart(ind_view, height=250)
        st.plotly_chart(fig_rsi, use_container_width=True)

with col2:
    if not ind_view.empty:
        fig_macd = create_macd_chart(ind_view, height=250)
        st.plotly_chart(fig_macd, use_container_width=True)

# Current indicator snapshot
if not indicators.empty:
    st.subheader("Current Indicators")
    latest = indicators.iloc[-1]

    col_a, col_b, col_c, col_d = st.columns(4)
    with col_a:
        rsi_val = latest.get("rsi_14")
        st.metric("RSI(14)", f"{rsi_val:.1f}" if pd.notna(rsi_val) else "—")
    with col_b:
        macd_val = latest.get("macd")
        st.metric("MACD", f"{macd_val:.4f}" if pd.notna(macd_val) else "—")
    with col_c:
        ema50 = latest.get("ema_50")
        close = prices.iloc[-1]["close"]
        if pd.notna(ema50):
            dist = (close - ema50) / ema50 * 100
            st.metric("EMA 50", f"${ema50:.2f}", f"{dist:+.1f}%")
        else:
            st.metric("EMA 50", "—")
    with col_d:
        vwap = latest.get("vwap_20")
        if pd.notna(vwap):
            st.metric("VWAP", f"${vwap:.2f}", "Above" if close > vwap else "Below")
        else:
            st.metric("VWAP", "—")

    col_e, col_f, col_g, col_h = st.columns(4)
    with col_e:
        bb_u = latest.get("bb_upper")
        bb_l = latest.get("bb_lower")
        if pd.notna(bb_u) and pd.notna(bb_l):
            st.metric("BB Upper", f"${bb_u:.2f}")
            st.metric("BB Lower", f"${bb_l:.2f}")
        else:
            st.metric("Bollinger Bands", "—")
    with col_f:
        atr = latest.get("atr_14")
        st.metric("ATR(14)", f"{atr:.2f}" if pd.notna(atr) else "—")
    with col_g:
        adx = latest.get("adx_14")
        plus_di = latest.get("plus_di")
        minus_di = latest.get("minus_di")
        if pd.notna(adx):
            st.metric("ADX(14)", f"{adx:.1f}", "Trending" if adx > 20 else "Weak")
            st.metric("+DI / -DI", f"{plus_di:.1f} / {minus_di:.1f}" if pd.notna(plus_di) else "—")
        else:
            st.metric("ADX", "—")
    with col_h:
        stoch_k = latest.get("stoch_k")
        stoch_d = latest.get("stoch_d")
        if pd.notna(stoch_k):
            zone = "Oversold" if stoch_k < 20 else ("Overbought" if stoch_k > 80 else "Neutral")
            st.metric("Stoch %K / %D", f"{stoch_k:.1f} / {stoch_d:.1f}" if pd.notna(stoch_d) else f"{stoch_k:.1f}", zone)
        else:
            st.metric("Stochastic", "—")

# Recent signals for this stock
st.subheader("Recent Signals")
if not signals.empty:
    sig_table = signals[["date", "signal_type", "direction", "price", "strategy"]].copy()
    sig_table["date"] = sig_table["date"].dt.strftime("%Y-%m-%d")
    sig_table.columns = ["Date", "Signal", "Direction", "Price", "Strategy"]
    st.dataframe(sig_table.head(20), use_container_width=True, hide_index=True)
else:
    st.info("No signals detected for this stock.")
