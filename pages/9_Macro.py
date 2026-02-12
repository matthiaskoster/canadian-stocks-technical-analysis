"""Page 9: Macro Dashboard — BoC rate, FRED economic series, and macro context."""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go

from data.database import get_macro, init_db
from config import FRED_SERIES

st.set_page_config(page_title="Macro Data", page_icon="🏛️", layout="wide")
st.title("Macro Dashboard")

init_db()

# All series we track (FRED + BoC)
ALL_MACRO = {
    "BOC_OVERNIGHT": "BoC Overnight Rate (%)",
    **FRED_SERIES,
}


@st.cache_data(ttl=300)
def load_macro(series_id):
    return get_macro(series_id)


# --- Summary metrics ---
st.subheader("Current Values")

cols = st.columns(len(ALL_MACRO))
for i, (series_id, name) in enumerate(ALL_MACRO.items()):
    df = load_macro(series_id)
    if not df.empty:
        latest = df.iloc[-1]
        val = latest["value"]
        # Format based on series type
        if "Rate" in name or "Yield" in name:
            display_val = f"{val:.2f}%"
        elif "USD" in name or "CAD" in name:
            display_val = f"{val:.4f}"
        else:
            display_val = f"${val:,.2f}"

        # Calculate change
        if len(df) >= 2:
            prev = df.iloc[-2]["value"]
            delta = val - prev
            if "Rate" in name or "Yield" in name:
                delta_str = f"{delta:+.2f}%"
            elif "USD" in name or "CAD" in name:
                delta_str = f"{delta:+.4f}"
            else:
                delta_str = f"${delta:+,.2f}"
        else:
            delta_str = None

        cols[i].metric(name, display_val, delta_str)
    else:
        cols[i].metric(name, "No data")

# --- Individual charts ---
st.subheader("Historical Charts")

time_range = st.radio(
    "Time Range", ["3M", "6M", "1Y", "2Y", "All"], horizontal=True, index=2,
)
cutoff_map = {"3M": 63, "6M": 126, "1Y": 252, "2Y": 504, "All": 99999}
n_days = cutoff_map[time_range]

# Color map for each series
colors = {
    "BOC_OVERNIGHT": "#ff9800",
    "DCOILWTICO": "#e91e63",
    "DEXCAUS": "#00bcd4",
    "DGS10": "#4caf50",
}

for series_id, name in ALL_MACRO.items():
    df = load_macro(series_id)
    if df.empty:
        continue

    df = df.sort_values("date").tail(n_days)

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df["date"], y=df["value"],
        mode="lines",
        name=name,
        line=dict(color=colors.get(series_id, "#ffffff"), width=2),
    ))

    # Format y-axis
    if "Rate" in name or "Yield" in name:
        yformat = ".2f"
        ysuffix = "%"
    elif "USD" in name or "CAD" in name:
        yformat = ".4f"
        ysuffix = ""
    else:
        yformat = ",.2f"
        ysuffix = ""

    fig.update_layout(
        template="plotly_dark",
        title=name,
        xaxis_title="Date",
        yaxis=dict(tickformat=yformat, ticksuffix=ysuffix),
        height=350,
        margin=dict(l=40, r=20, t=50, b=40),
    )
    st.plotly_chart(fig, use_container_width=True)

# --- Overlay: BoC rate vs Bank stocks ---
st.subheader("BoC Rate vs Bank Stock Performance")

boc_df = load_macro("BOC_OVERNIGHT")
if not boc_df.empty:
    from data.database import get_prices
    from config import BANKS

    boc_df = boc_df.sort_values("date").tail(n_days)

    fig2 = go.Figure()

    # BoC rate on secondary y-axis
    fig2.add_trace(go.Scatter(
        x=boc_df["date"], y=boc_df["value"],
        mode="lines",
        name="BoC Overnight Rate (%)",
        line=dict(color="#ff9800", width=3),
        yaxis="y2",
    ))

    # Normalized bank stock prices
    bank_colors = ["#2196f3", "#4caf50", "#e91e63", "#9c27b0",
                   "#00bcd4", "#ffeb3b", "#ff5722", "#795548"]
    min_date = boc_df["date"].min()
    for i, (ticker, name) in enumerate(BANKS.items()):
        stock_df = get_prices(ticker)
        if stock_df.empty:
            continue
        stock_df = stock_df.sort_values("date")
        stock_df = stock_df[stock_df["date"] >= min_date].tail(n_days)
        if stock_df.empty:
            continue
        base = stock_df.iloc[0]["close"]
        stock_df["normalized"] = stock_df["close"] / base * 100
        fig2.add_trace(go.Scatter(
            x=stock_df["date"], y=stock_df["normalized"],
            mode="lines",
            name=f"{ticker}",
            line=dict(color=bank_colors[i % len(bank_colors)], width=1.5),
        ))

    fig2.update_layout(
        template="plotly_dark",
        title="BoC Rate vs Bank Stocks (indexed to 100)",
        xaxis_title="Date",
        yaxis=dict(title="Stock Price (indexed)", side="left"),
        yaxis2=dict(title="BoC Rate (%)", side="right", overlaying="y",
                    tickformat=".2f", ticksuffix="%"),
        height=500,
        margin=dict(l=40, r=60, t=50, b=40),
        legend=dict(orientation="h", yanchor="bottom", y=-0.35),
    )
    st.plotly_chart(fig2, use_container_width=True)
else:
    st.info("No BoC rate data. Run `python3 main.py` to fetch.")
