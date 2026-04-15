"""Page 12: AI Stocks Overview — US AI stock universe grouped by sub-sector."""

import streamlit as st
import pandas as pd
from datetime import date

from data.database import get_latest_prices, get_indicators, get_signals, get_earnings, init_db
from dashboard.components.tables import (
    style_rsi, style_macd_status, style_direction,
    get_ma_distance, get_macd_status, get_vwap_position,
)
from dashboard.components.styles import apply_custom_css
from config import AI_ALL_STOCKS, AI_SECTORS, AI_SECTOR_GROUPS, AI_TICKERS

st.set_page_config(page_title="AI Stocks Overview", page_icon="🤖", layout="wide")
apply_custom_css()
st.title("AI Stocks Overview")
st.caption("US-listed AI stocks — prices in USD. Run `python3 main.py --universe ai` to refresh.")

init_db()


@st.cache_data(ttl=300)
def load_ai_data():
    prices = get_latest_prices()
    indicators = get_indicators()
    signals = get_signals(limit=500)
    earnings = get_earnings()
    return prices, indicators, signals, earnings


prices, indicators, signals, earnings = load_ai_data()

# Filter to AI tickers only
ai_prices = prices[prices["ticker"].isin(AI_TICKERS)]

if ai_prices.empty:
    st.warning("No AI stock data found. Run `python3 main.py --universe ai` first.")
    st.stop()

# Build earnings lookup: ticker → earnings_date
earnings_map = {}
if not earnings.empty:
    for _, row in earnings.iterrows():
        if row["ticker"] in AI_TICKERS:
            earnings_map[row["ticker"]] = row["earnings_date"]

today = pd.Timestamp.now().normalize()
two_weeks = today + pd.Timedelta(days=14)


def earnings_soon(ticker):
    """Return True if earnings are within the next 14 days."""
    d = earnings_map.get(ticker)
    if d is None:
        return False
    try:
        return today <= pd.Timestamp(d) <= two_weeks
    except Exception:
        return False


def format_earnings(ticker):
    d = earnings_map.get(ticker)
    if d is None:
        return "—"
    try:
        return pd.Timestamp(d).strftime("%Y-%m-%d")
    except Exception:
        return str(d)


def style_earnings(val):
    """Highlight upcoming earnings in orange."""
    if val == "—":
        return ""
    try:
        d = pd.Timestamp(val)
        if today <= d <= two_weeks:
            return "color: #ff9800; font-weight: bold"
    except Exception:
        pass
    return ""


def style_pct_distance(val):
    """Green if positive (above MA), red if negative (below MA)."""
    if val == "—":
        return ""
    try:
        num = float(val.replace("%", "").replace("+", ""))
        if num > 0:
            return "color: #26a69a"
        elif num < 0:
            return "color: #ef5350"
    except Exception:
        pass
    return ""


def style_vwap(val):
    if val == "Above":
        return "color: #26a69a"
    elif val == "Below":
        return "color: #ef5350"
    return ""


# ── Summary metrics ──────────────────────────────────────────────────────────
total = len(ai_prices)
with_data = len(ai_prices[ai_prices["close"].notna()])
upcoming_earnings = sum(1 for t in AI_TICKERS if earnings_soon(t))

c1, c2, c3, c4 = st.columns(4)
c1.metric("Stocks Tracked", with_data)
c2.metric("Sub-sectors", len(AI_SECTOR_GROUPS))
c3.metric("Earnings Next 14d", upcoming_earnings)
c4.metric("Total AI Universe", len(AI_TICKERS))

st.divider()

# ── Sector tabs ───────────────────────────────────────────────────────────────
tab_names = [name for name, _ in AI_SECTOR_GROUPS] + ["All Sectors"]
tabs = st.tabs(tab_names)

for tab, (sector_name, sector_dict) in zip(tabs[:-1], AI_SECTOR_GROUPS):
    with tab:
        sector_tickers = list(sector_dict.keys())
        rows = []

        for ticker in sector_tickers:
            price_row = ai_prices[ai_prices["ticker"] == ticker]
            if price_row.empty:
                continue
            price_row = price_row.iloc[0]

            tk_ind = indicators[indicators["ticker"] == ticker]
            if tk_ind.empty:
                continue
            latest = tk_ind.iloc[-1]

            close = price_row["close"]
            ema_50 = latest.get("ema_50")
            ema_200 = latest.get("ema_200")
            rsi_14 = latest.get("rsi_14")
            macd_val = latest.get("macd")
            macd_sig = latest.get("macd_signal")
            vwap = latest.get("vwap_20")
            bb_upper = latest.get("bb_upper")
            bb_lower = latest.get("bb_lower")
            adx = latest.get("adx_14")

            # BB position
            if pd.notna(bb_upper) and pd.notna(bb_lower) and pd.notna(close):
                bb_width = bb_upper - bb_lower
                bb_pos = ((close - bb_lower) / bb_width * 100) if bb_width > 0 else None
                bb_pos_str = f"{bb_pos:.0f}%" if bb_pos is not None else "—"
            else:
                bb_pos_str = "—"

            rows.append({
                "Ticker": ticker,
                "Company": AI_ALL_STOCKS.get(ticker, ""),
                "Price (USD)": round(close, 2) if pd.notna(close) else None,
                "Dist EMA50": get_ma_distance(close, ema_50),
                "Dist EMA200": get_ma_distance(close, ema_200),
                "RSI(14)": round(rsi_14, 1) if pd.notna(rsi_14) else None,
                "MACD": get_macd_status(macd_val, macd_sig),
                "VWAP": get_vwap_position(close, vwap),
                "BB Position": bb_pos_str,
                "ADX": round(adx, 1) if pd.notna(adx) else None,
                "Earnings": format_earnings(ticker),
            })

        if not rows:
            st.info(f"No data for {sector_name} yet.")
            continue

        df = pd.DataFrame(rows)
        styled = (
            df.style
            .map(style_rsi, subset=["RSI(14)"])
            .map(style_macd_status, subset=["MACD"])
            .map(style_pct_distance, subset=["Dist EMA50", "Dist EMA200"])
            .map(style_vwap, subset=["VWAP"])
            .map(style_earnings, subset=["Earnings"])
            .format({"Price (USD)": "${:.2f}"}, na_rep="—")
        )
        st.dataframe(styled, use_container_width=True, hide_index=True)

# ── All Sectors tab ───────────────────────────────────────────────────────────
with tabs[-1]:
    all_rows = []
    for ticker in AI_TICKERS:
        price_row = ai_prices[ai_prices["ticker"] == ticker]
        if price_row.empty:
            continue
        price_row = price_row.iloc[0]

        tk_ind = indicators[indicators["ticker"] == ticker]
        if tk_ind.empty:
            continue
        latest = tk_ind.iloc[-1]

        close = price_row["close"]
        ema_50 = latest.get("ema_50")
        ema_200 = latest.get("ema_200")
        rsi_14 = latest.get("rsi_14")
        macd_val = latest.get("macd")
        macd_sig = latest.get("macd_signal")
        vwap = latest.get("vwap_20")

        all_rows.append({
            "Ticker": ticker,
            "Company": AI_ALL_STOCKS.get(ticker, ""),
            "Sub-sector": AI_SECTORS.get(ticker, ""),
            "Price (USD)": round(close, 2) if pd.notna(close) else None,
            "Dist EMA50": get_ma_distance(close, ema_50),
            "Dist EMA200": get_ma_distance(close, ema_200),
            "RSI(14)": round(rsi_14, 1) if pd.notna(rsi_14) else None,
            "MACD": get_macd_status(macd_val, macd_sig),
            "VWAP": get_vwap_position(close, vwap),
            "Earnings": format_earnings(ticker),
        })

    if all_rows:
        df_all = pd.DataFrame(all_rows)

        # Optional: filter by sub-sector
        sector_filter = st.multiselect(
            "Filter sub-sectors",
            options=sorted(df_all["Sub-sector"].unique()),
            default=sorted(df_all["Sub-sector"].unique()),
        )
        df_all = df_all[df_all["Sub-sector"].isin(sector_filter)]

        styled_all = (
            df_all.style
            .map(style_rsi, subset=["RSI(14)"])
            .map(style_macd_status, subset=["MACD"])
            .map(style_pct_distance, subset=["Dist EMA50", "Dist EMA200"])
            .map(style_vwap, subset=["VWAP"])
            .map(style_earnings, subset=["Earnings"])
            .format({"Price (USD)": "${:.2f}"}, na_rep="—")
        )
        st.dataframe(styled_all, use_container_width=True, hide_index=True, height=700)

# ── Recent AI Signals ─────────────────────────────────────────────────────────
st.divider()
st.subheader("Recent AI Stock Signals")

ai_signals = signals[signals["ticker"].isin(AI_TICKERS)]

if not ai_signals.empty:
    sig_display = ai_signals[["date", "ticker", "signal_type", "direction", "price", "strategy"]].copy()
    sig_display["date"] = sig_display["date"].dt.strftime("%Y-%m-%d")
    sig_display["Company"] = sig_display["ticker"].map(AI_ALL_STOCKS)
    sig_display = sig_display[["date", "ticker", "Company", "signal_type", "direction", "price", "strategy"]]
    sig_display.columns = ["Date", "Ticker", "Company", "Signal", "Direction", "Price (USD)", "Strategy"]

    styled_sig = (
        sig_display.head(50).style
        .map(style_direction, subset=["Direction"])
        .format({"Price (USD)": "${:.2f}"}, na_rep="—")
    )
    st.dataframe(styled_sig, use_container_width=True, hide_index=True)
else:
    st.info("No signals yet. Run the pipeline to generate signals.")
