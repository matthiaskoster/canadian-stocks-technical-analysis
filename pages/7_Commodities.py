"""Page 7: Commodities — Commodity price tracking and stock correlation."""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go

from data.database import get_prices, init_db
from dashboard.components.styles import apply_custom_css
from config import COMMODITIES, COMMODITY_TICKERS, COMMODITY_STOCK_MAP, ALL_STOCKS

st.set_page_config(page_title="Commodities", page_icon="🛢️", layout="wide")
apply_custom_css()
st.title("Commodity Prices")

init_db()


@st.cache_data(ttl=300)
def load_commodity_prices():
    """Load price data for all commodities."""
    frames = {}
    for ticker in COMMODITY_TICKERS:
        df = get_prices(ticker)
        if not df.empty:
            frames[ticker] = df
    return frames


commodity_data = load_commodity_prices()

if not commodity_data:
    st.warning("No commodity data. Run `python3 main.py` to fetch data.")
    st.stop()

# --- Summary table ---
st.subheader("Summary")

summary_rows = []
for ticker in COMMODITY_TICKERS:
    df = commodity_data.get(ticker)
    if df is None or len(df) < 2:
        continue
    df_sorted = df.sort_values("date")
    latest = df_sorted.iloc[-1]
    prev = df_sorted.iloc[-2]
    price = latest["close"]
    daily_chg = (price - prev["close"]) / prev["close"] * 100

    # 1-week change (5 trading days)
    if len(df_sorted) >= 6:
        week_ago = df_sorted.iloc[-6]["close"]
        week_chg = (price - week_ago) / week_ago * 100
    else:
        week_chg = None

    summary_rows.append({
        "Commodity": COMMODITIES[ticker],
        "Ticker": ticker,
        "Price": price,
        "Daily Chg %": daily_chg,
        "1W Chg %": week_chg,
        "Date": latest["date"].strftime("%Y-%m-%d"),
    })

if summary_rows:
    summary_df = pd.DataFrame(summary_rows)

    def style_change(val):
        if pd.isna(val):
            return ""
        if val > 0:
            return "color: #00c853"
        elif val < 0:
            return "color: #ff1744"
        return ""

    styled = summary_df.style.applymap(
        style_change, subset=["Daily Chg %", "1W Chg %"]
    ).format({
        "Price": "${:,.2f}",
        "Daily Chg %": "{:+.2f}%",
        "1W Chg %": "{:+.2f}%",
    }, na_rep="—")
    st.dataframe(styled, use_container_width=True, hide_index=True)

# --- Individual commodity chart ---
st.subheader("Price History")

commodity_options = [t for t in COMMODITY_TICKERS if t in commodity_data]
selected = st.selectbox(
    "Select Commodity",
    commodity_options,
    format_func=lambda t: f"{COMMODITIES[t]} ({t})",
)

time_range = st.radio(
    "Time Range", ["1M", "3M", "6M", "1Y", "All"], horizontal=True, index=3,
)
cutoff_map = {"1M": 21, "3M": 63, "6M": 126, "1Y": 252, "All": 99999}
n_days = cutoff_map[time_range]

df = commodity_data[selected].sort_values("date").tail(n_days)

fig = go.Figure()
fig.add_trace(go.Scatter(
    x=df["date"], y=df["close"],
    mode="lines",
    name=COMMODITIES[selected],
    line=dict(color="#00bcd4", width=2),
))
fig.update_layout(
    template="plotly_white",
    title=f"{COMMODITIES[selected]} — Close Price",
    xaxis_title="Date",
    yaxis_title="Price (USD)",
    height=450,
    margin=dict(l=40, r=20, t=50, b=40),
    paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
)
st.plotly_chart(fig, use_container_width=True)

# --- Commodity vs Related Stocks (normalized overlay) ---
related = COMMODITY_STOCK_MAP.get(selected, [])
if related:
    st.subheader(f"{COMMODITIES[selected]} vs Related Stocks (Normalized)")

    # Rebase all series to 100 at the start of the visible window
    fig2 = go.Figure()

    # Commodity series
    comm_df = df.copy()
    if not comm_df.empty:
        base = comm_df.iloc[0]["close"]
        comm_df["normalized"] = comm_df["close"] / base * 100
        fig2.add_trace(go.Scatter(
            x=comm_df["date"], y=comm_df["normalized"],
            mode="lines",
            name=COMMODITIES[selected],
            line=dict(width=3),
        ))

    # Related stock series
    colors = ["#ff9800", "#e91e63", "#4caf50", "#9c27b0", "#ffeb3b", "#00e5ff"]
    for i, stock_ticker in enumerate(related):
        stock_df = get_prices(stock_ticker)
        if stock_df.empty:
            continue
        stock_df = stock_df.sort_values("date")
        # Align to commodity date range
        min_date = comm_df["date"].min()
        stock_df = stock_df[stock_df["date"] >= min_date].tail(n_days)
        if stock_df.empty:
            continue
        base = stock_df.iloc[0]["close"]
        stock_df["normalized"] = stock_df["close"] / base * 100
        label = f"{stock_ticker} — {ALL_STOCKS.get(stock_ticker, '')}"
        fig2.add_trace(go.Scatter(
            x=stock_df["date"], y=stock_df["normalized"],
            mode="lines",
            name=label,
            line=dict(color=colors[i % len(colors)], width=2),
        ))

    fig2.update_layout(
        template="plotly_white",
        title=f"Normalized Performance (rebased to 100)",
        xaxis_title="Date",
        yaxis_title="Indexed (100 = start)",
        height=500,
        margin=dict(l=40, r=20, t=50, b=40),
        legend=dict(orientation="h", yanchor="bottom", y=-0.3),
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
    )
    st.plotly_chart(fig2, use_container_width=True)
