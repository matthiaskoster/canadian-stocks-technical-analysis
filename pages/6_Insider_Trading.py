"""Page 6: Insider Trading — Insider buy/sell activity for all tracked stocks."""

import streamlit as st
import pandas as pd

from data.database import get_insider_trades, init_db
from data.data_fetcher import fetch_usdcad_rate
from config import ALL_STOCKS, SECTORS

st.set_page_config(page_title="Insider Trading", page_icon="👔", layout="wide")
st.title("Insider Trading Activity")

init_db()


@st.cache_data(ttl=300)
def load_insider_data():
    return get_insider_trades()


@st.cache_data(ttl=3600)
def load_fx_rate():
    rate = fetch_usdcad_rate()
    return rate if rate else 1.36  # fallback


trades_df = load_insider_data()

if trades_df.empty:
    st.warning("No insider trading data. Run `python main.py` to fetch data.")
    st.stop()

usdcad = load_fx_rate()


def compute_cad_price_per_share(row):
    """Compute price-per-share in CAD. Yahoo reports all .TO insider data in USD."""
    shares = row["shares"]
    value = row["value"]
    if pd.isna(shares) or pd.isna(value) or shares == 0:
        return None

    pps_usd = value / shares
    return round(pps_usd * usdcad, 2)


# Add CAD price-per-share and converted value columns
trades_df = trades_df.copy()
trades_df["cad_pps"] = trades_df.apply(compute_cad_price_per_share, axis=1)


def compute_cad_value(row):
    """Recompute value in CAD using the CAD price-per-share."""
    if pd.isna(row["cad_pps"]) or pd.isna(row["shares"]) or row["shares"] == 0:
        return row["value"]
    return round(row["cad_pps"] * abs(row["shares"]), 2)


trades_df["value_cad"] = trades_df.apply(compute_cad_value, axis=1)

# --- Filters ---
col_filter1, col_filter2, col_filter3 = st.columns(3)

with col_filter1:
    sector_options = ["All"] + sorted(set(SECTORS.values()))
    sector_filter = st.selectbox("Sector", sector_options)

with col_filter2:
    if sector_filter == "All":
        available_tickers = sorted(trades_df["ticker"].unique())
    else:
        sector_tickers = [t for t, s in SECTORS.items() if s == sector_filter]
        available_tickers = sorted([t for t in trades_df["ticker"].unique() if t in sector_tickers])
    ticker_options = ["All stocks"] + available_tickers
    ticker_filter = st.selectbox("Ticker", ticker_options)

with col_filter3:
    txn_type_filter = st.selectbox("Transaction type", ["All", "Buys only", "Sells only"])

# Apply filters
filtered = trades_df.copy()

if sector_filter != "All":
    sector_tickers = [t for t, s in SECTORS.items() if s == sector_filter]
    filtered = filtered[filtered["ticker"].isin(sector_tickers)]

if ticker_filter != "All stocks":
    filtered = filtered[filtered["ticker"] == ticker_filter]


# Classify transactions as buy or sell
def classify_txn(txn_type):
    if pd.isna(txn_type):
        return "Other"
    t = str(txn_type).lower()
    if any(kw in t for kw in ["purchase", "buy", "acquisition"]):
        return "Buy"
    elif any(kw in t for kw in ["sale", "sell", "disposition"]):
        return "Sell"
    return "Other"


filtered["direction"] = filtered["transaction_type"].apply(classify_txn)

if txn_type_filter == "Buys only":
    filtered = filtered[filtered["direction"] == "Buy"]
elif txn_type_filter == "Sells only":
    filtered = filtered[filtered["direction"] == "Sell"]

# --- Summary metrics ---
st.subheader("Summary")

total_buys = len(filtered[filtered["direction"] == "Buy"])
total_sells = len(filtered[filtered["direction"] == "Sell"])
buy_value = filtered.loc[filtered["direction"] == "Buy", "value_cad"].sum()
sell_value = filtered.loc[filtered["direction"] == "Sell", "value_cad"].sum()

col1, col2, col3, col4, col5 = st.columns(5)
col1.metric("Buy Transactions", f"{total_buys:,}")
col2.metric("Sell Transactions", f"{total_sells:,}")
col3.metric("Buy Value (CAD)", f"${buy_value:,.0f}" if pd.notna(buy_value) else "N/A")
col4.metric("Sell Value (CAD)", f"${sell_value:,.0f}" if pd.notna(sell_value) else "N/A")
col5.metric("USD/CAD Rate", f"{usdcad:.4f}")

# --- Summary by stock ---
st.subheader("Activity by Stock")

summary_rows = []
for ticker in sorted(filtered["ticker"].unique()):
    tk_data = filtered[filtered["ticker"] == ticker]
    buys = tk_data[tk_data["direction"] == "Buy"]
    sells = tk_data[tk_data["direction"] == "Sell"]
    summary_rows.append({
        "Ticker": ticker,
        "Name": ALL_STOCKS.get(ticker, ""),
        "Sector": SECTORS.get(ticker, ""),
        "Buy Txns": len(buys),
        "Sell Txns": len(sells),
        "Buy Value (CAD)": buys["value_cad"].sum() if not buys.empty else 0,
        "Sell Value (CAD)": sells["value_cad"].sum() if not sells.empty else 0,
        "Net Sentiment": "Bullish" if len(buys) > len(sells) else ("Bearish" if len(sells) > len(buys) else "Neutral"),
    })

if summary_rows:
    summary_df = pd.DataFrame(summary_rows)

    def style_sentiment(val):
        if val == "Bullish":
            return "color: #00c853"
        elif val == "Bearish":
            return "color: #ff1744"
        return ""

    styled_summary = summary_df.style.applymap(style_sentiment, subset=["Net Sentiment"])
    styled_summary = styled_summary.format({
        "Buy Value (CAD)": "${:,.0f}",
        "Sell Value (CAD)": "${:,.0f}",
    }, na_rep="—")
    st.dataframe(styled_summary, use_container_width=True, hide_index=True)

# --- Detailed transactions ---
st.subheader("Transaction Details")

if not filtered.empty:
    display_df = filtered[["ticker", "date", "insider", "position", "transaction_type",
                           "direction", "shares", "cad_pps", "value_cad", "ownership"]].copy()
    display_df["date"] = display_df["date"].dt.strftime("%Y-%m-%d")
    display_df.columns = ["Ticker", "Date", "Insider", "Position", "Transaction",
                          "Direction", "Shares", "CAD/Share", "Value (CAD)", "Ownership"]

    def style_direction(val):
        if val == "Buy":
            return "color: #00c853"
        elif val == "Sell":
            return "color: #ff1744"
        return ""

    styled_detail = display_df.style.applymap(style_direction, subset=["Direction"])
    styled_detail = styled_detail.format({
        "Shares": "{:,.0f}",
        "CAD/Share": "${:,.2f}",
        "Value (CAD)": "${:,.0f}",
    }, na_rep="—")
    st.dataframe(styled_detail, use_container_width=True, hide_index=True, height=600)
else:
    st.info("No transactions match the current filters.")
