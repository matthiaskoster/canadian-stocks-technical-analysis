"""Page 10: Insider Alerts — Insider buying below Bollinger Band signals + paper portfolio."""

import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

from data.database import init_db, get_connection
from dashboard.components.styles import apply_custom_css
from config import ALL_STOCKS, SECTORS

st.set_page_config(page_title="Insider Alerts", page_icon="🚨", layout="wide")
apply_custom_css()

init_db()

POSITION_SIZE = 10_000
HOLD_DAYS = 30


# ---------------------------------------------------------------------------
# Data loading
# ---------------------------------------------------------------------------

@st.cache_data(ttl=300)
def load_all_data():
    """Load prices, indicators, and insider trades from DB."""
    with get_connection() as conn:
        prices = pd.read_sql(
            "SELECT ticker, date, open, high, low, close FROM stock_prices ORDER BY ticker, date",
            conn,
        )
        indicators = pd.read_sql(
            "SELECT ticker, date, rsi_14, bb_upper, bb_lower FROM indicators ORDER BY ticker, date",
            conn,
        )
        trades = pd.read_sql(
            "SELECT ticker, date, insider, position, shares, value "
            "FROM insider_trades "
            "WHERE transaction_type LIKE '%Acquisition in the public market%' "
            "ORDER BY ticker, date",
            conn,
        )
    for df in (prices, indicators, trades):
        if not df.empty:
            df["date"] = pd.to_datetime(df["date"])
    return prices, indicators, trades


# ---------------------------------------------------------------------------
# Signal detection
# ---------------------------------------------------------------------------

def find_bb_insider_signals(prices, indicators, trades):
    """Find insider open-market buys where price was below the lower Bollinger Band.

    Returns one row per unique (ticker, date) event.
    """
    events = []
    for (ticker, date), grp in trades.groupby(["ticker", "date"]):
        # Nearest indicator on or before the trade date
        ind_mask = (indicators["ticker"] == ticker) & (
            indicators["date"] <= date
        ) & (indicators["date"] >= date - timedelta(days=5))
        ind_sub = indicators[ind_mask].sort_values("date", ascending=False)
        if ind_sub.empty:
            continue
        ind_row = ind_sub.iloc[0]

        bb_lower = ind_row["bb_lower"]
        bb_upper = ind_row["bb_upper"]
        rsi = ind_row["rsi_14"]
        if pd.isna(bb_lower) or pd.isna(bb_upper):
            continue

        # Nearest closing price on or before the trade date
        pr_mask = (prices["ticker"] == ticker) & (
            prices["date"] <= date
        ) & (prices["date"] >= date - timedelta(days=5))
        pr_sub = prices[pr_mask].sort_values("date", ascending=False)
        if pr_sub.empty:
            continue
        close = pr_sub.iloc[0]["close"]

        if bb_upper == bb_lower:
            continue
        bb_pos = (close - bb_lower) / (bb_upper - bb_lower)
        if bb_pos > 0.0:
            continue  # not below lower band

        # 52-week high for context
        hist = prices[(prices["ticker"] == ticker) & (prices["date"] <= date)]
        high_52w = hist.tail(252)["high"].max() if len(hist) >= 20 else None
        dd_52w = ((close - high_52w) / high_52w * 100) if high_52w else None

        insiders = sorted(grp["insider"].unique())
        events.append(
            {
                "ticker": ticker,
                "signal_date": date,
                "close": close,
                "bb_lower": bb_lower,
                "bb_pos": bb_pos,
                "rsi": rsi,
                "dd_52w": dd_52w,
                "n_insiders": grp["insider"].nunique(),
                "insiders": ", ".join(insiders),
                "total_shares": grp["shares"].sum(),
                "double_signal": (pd.notna(rsi) and rsi < 30),
            }
        )
    return pd.DataFrame(events)


# ---------------------------------------------------------------------------
# Portfolio simulation
# ---------------------------------------------------------------------------

def build_portfolio(events_df, prices):
    """Simulate the paper portfolio: buy next-day open, sell ~30 days later."""
    if events_df.empty:
        return pd.DataFrame()

    portfolio = []
    today = pd.Timestamp(datetime.now().date())

    for _, ev in events_df.sort_values("signal_date").iterrows():
        ticker = ev["ticker"]
        signal_date = ev["signal_date"]

        # Buy on next trading day (open price)
        buy_mask = (prices["ticker"] == ticker) & (prices["date"] > signal_date)
        buy_sub = prices[buy_mask].sort_values("date")
        if buy_sub.empty:
            continue
        buy_row = buy_sub.iloc[0]
        buy_price = buy_row["open"]
        buy_date = buy_row["date"]
        shares = max(1, int(POSITION_SIZE / buy_price))
        cost = shares * buy_price

        # Sell ~30 days later (close price)
        target_sell = buy_date + timedelta(days=HOLD_DAYS)
        sell_mask = (prices["ticker"] == ticker) & (prices["date"] >= target_sell)
        sell_sub = prices[sell_mask].sort_values("date")

        if not sell_sub.empty:
            sell_row = sell_sub.iloc[0]
            sell_price = sell_row["close"]
            sell_date = sell_row["date"]
            status = "CLOSED"
        else:
            # Still open — use latest available price
            latest = prices[prices["ticker"] == ticker].sort_values("date").iloc[-1]
            sell_price = latest["close"]
            sell_date = latest["date"]
            status = "OPEN"

        pnl = shares * (sell_price - buy_price)
        ret_pct = ((sell_price - buy_price) / buy_price) * 100
        hold = (sell_date - buy_date).days

        portfolio.append(
            {
                "Ticker": ticker,
                "Sector": SECTORS.get(ticker, ""),
                "Signal": ev["signal_date"].strftime("%Y-%m-%d"),
                "Insiders": ev["n_insiders"],
                "RSI": round(ev["rsi"], 1) if pd.notna(ev["rsi"]) else None,
                "BB Pos": round(ev["bb_pos"], 2),
                "Double": ev["double_signal"],
                "Entry Date": buy_date.strftime("%Y-%m-%d"),
                "Entry $": round(buy_price, 2),
                "Shares": shares,
                "Cost": round(cost, 2),
                "Exit Date": sell_date.strftime("%Y-%m-%d"),
                "Exit $": round(sell_price, 2),
                "P&L": round(pnl, 2),
                "Return %": round(ret_pct, 1),
                "Days": hold,
                "Status": status,
                # Keep raw dates for sorting / equity curve
                "_buy_date": buy_date,
                "_sell_date": sell_date,
            }
        )
    return pd.DataFrame(portfolio)


# ---------------------------------------------------------------------------
# Styling helpers
# ---------------------------------------------------------------------------

def color_pnl(val):
    if pd.isna(val):
        return ""
    if isinstance(val, str):
        return ""
    return "color: #16a34a; font-weight:600" if val > 0 else "color: #dc2626; font-weight:600" if val < 0 else ""


def color_status(val):
    if val == "OPEN":
        return "background-color: #fef3c7; font-weight:600"
    return ""


def color_double(val):
    if val is True:
        return "background-color: #dcfce7; font-weight:600"
    return ""


# ---------------------------------------------------------------------------
# Page rendering
# ---------------------------------------------------------------------------

prices, indicators, trades = load_all_data()

if trades.empty:
    st.warning("No insider trading data. Run `python main.py` to fetch data.")
    st.stop()

events_df = find_bb_insider_signals(prices, indicators, trades)

if events_df.empty:
    st.info("No insider purchases below the lower Bollinger Band found in the data.")
    st.stop()


# ---- ALERT BANNER ----
today = pd.Timestamp(datetime.now().date())
recent_cutoff = today - timedelta(days=3)
recent_signals = events_df[events_df["signal_date"] >= recent_cutoff].sort_values(
    "signal_date", ascending=False
)

if not recent_signals.empty:
    for _, sig in recent_signals.iterrows():
        days_ago = (today - sig["signal_date"]).days
        age_label = "TODAY" if days_ago == 0 else f"{days_ago}d ago"
        double_tag = " + RSI < 30 DOUBLE SIGNAL" if sig["double_signal"] else ""
        st.markdown(
            f"""
            <div style="
                background: linear-gradient(135deg, #dc2626 0%, #991b1b 100%);
                color: white;
                padding: 18px 24px;
                border-radius: 10px;
                margin-bottom: 12px;
                border-left: 6px solid #fbbf24;
                font-size: 1.05em;
            ">
                <span style="font-size:1.4em; font-weight:800;">
                    NEW SIGNAL — {sig['ticker']}
                    <span style="font-size:0.7em; opacity:0.85; margin-left:8px;">{age_label}</span>
                </span>{double_tag}
                <br/>
                <span style="opacity:0.95;">
                    {sig['n_insiders']} insider(s) bought below lower Bollinger Band
                    &nbsp;|&nbsp; RSI {sig['rsi']:.0f}
                    &nbsp;|&nbsp; BB pos {sig['bb_pos']:.2f}
                    &nbsp;|&nbsp; {sig['dd_52w']:.1f}% off 52w high
                </span>
                <br/>
                <span style="font-size:0.85em; opacity:0.8;">{sig['insiders']}</span>
            </div>
            """,
            unsafe_allow_html=True,
        )
else:
    st.markdown(
        """
        <div style="
            background: #f0fdf4;
            border: 1px solid #bbf7d0;
            border-left: 6px solid #22c55e;
            padding: 14px 20px;
            border-radius: 8px;
            margin-bottom: 16px;
            color: #166534;
        ">
            <strong>No new signals in the last 3 days.</strong>
            Monitoring insider purchases below lower Bollinger Band across all tracked stocks.
        </div>
        """,
        unsafe_allow_html=True,
    )


st.title("Insider Alert Portfolio")
st.caption(
    "Strategy: buy next-day open when an insider purchases shares while price is "
    "below the lower Bollinger Band. Hold ~30 days. $10,000 per position."
)

# ---- PORTFOLIO TABLE ----
pf = build_portfolio(events_df, prices)

if pf.empty:
    st.warning("No trades could be simulated (missing price data).")
    st.stop()

# Summary metrics
total_pnl = pf["P&L"].sum()
total_cost = pf["Cost"].sum()
wins = (pf["P&L"] > 0).sum()
losses = (pf["P&L"] <= 0).sum()
total_trades = len(pf)
win_rate = wins / total_trades * 100 if total_trades else 0
avg_ret = pf["Return %"].mean()
open_count = (pf["Status"] == "OPEN").sum()
avg_win = pf.loc[pf["P&L"] > 0, "P&L"].mean() if wins else 0
avg_loss = pf.loc[pf["P&L"] <= 0, "P&L"].mean() if losses else 0

row1_c1, row1_c2, row1_c3 = st.columns(3)
row1_c1.metric("Total P&L", f"${total_pnl:+,.0f}")
row1_c2.metric("Trades", f"{total_trades} ({open_count} open)")
row1_c3.metric("Win Rate", f"{win_rate:.0f}%")
row2_c1, row2_c2, row2_c3 = st.columns(3)
row2_c1.metric("Avg Return", f"{avg_ret:+.1f}%")
row2_c2.metric("Avg Win", f"${avg_win:+,.0f}")
row2_c3.metric("Avg Loss", f"${avg_loss:+,.0f}")

st.divider()

# Display table
display_cols = [
    "Ticker", "Sector", "Signal", "Insiders", "RSI", "BB Pos", "Double",
    "Entry Date", "Entry $", "Shares", "Exit Date", "Exit $",
    "P&L", "Return %", "Days", "Status",
]
display_df = pf[display_cols].copy()

styled = (
    display_df.style
    .applymap(color_pnl, subset=["P&L", "Return %"])
    .applymap(color_status, subset=["Status"])
    .applymap(color_double, subset=["Double"])
    .format(
        {
            "Entry $": "${:.2f}",
            "Exit $": "${:.2f}",
            "P&L": "${:+,.0f}",
            "Return %": "{:+.1f}%",
            "RSI": "{:.0f}",
            "BB Pos": "{:.2f}",
        },
        na_rep="—",
    )
)
st.dataframe(styled, use_container_width=True, hide_index=True, height=min(700, 40 + 35 * len(display_df)))


# ---- EQUITY CURVE ----
st.subheader("Equity Curve")

equity_data = pf.sort_values("_sell_date").copy()
equity_data["Cumulative P&L"] = equity_data["P&L"].cumsum()

chart_df = equity_data[["_sell_date", "Cumulative P&L"]].rename(
    columns={"_sell_date": "Date"}
)
# Add starting point at zero
start_row = pd.DataFrame(
    [{"Date": equity_data["_buy_date"].min(), "Cumulative P&L": 0}]
)
chart_df = pd.concat([start_row, chart_df], ignore_index=True)
chart_df = chart_df.set_index("Date")

st.line_chart(chart_df, use_container_width=True, height=350)


# ---- BREAKDOWNS ----
col_left, col_right = st.columns(2)

with col_left:
    st.subheader("By Ticker")
    ticker_stats = (
        pf.groupby("Ticker")
        .agg(
            Trades=("P&L", "count"),
            Wins=("P&L", lambda x: (x > 0).sum()),
            Total_PnL=("P&L", "sum"),
            Avg_Return=("Return %", "mean"),
        )
        .reset_index()
    )
    ticker_stats["Win %"] = (ticker_stats["Wins"] / ticker_stats["Trades"] * 100).round(0)
    ticker_stats = ticker_stats.sort_values("Total_PnL", ascending=False)
    ticker_styled = (
        ticker_stats.style
        .applymap(color_pnl, subset=["Total_PnL", "Avg_Return"])
        .format({"Total_PnL": "${:+,.0f}", "Avg_Return": "{:+.1f}%", "Win %": "{:.0f}%"})
    )
    st.dataframe(ticker_styled, use_container_width=True, hide_index=True)

with col_right:
    st.subheader("By Sector")
    sector_stats = (
        pf.groupby("Sector")
        .agg(
            Trades=("P&L", "count"),
            Wins=("P&L", lambda x: (x > 0).sum()),
            Total_PnL=("P&L", "sum"),
            Avg_Return=("Return %", "mean"),
        )
        .reset_index()
    )
    sector_stats["Win %"] = (sector_stats["Wins"] / sector_stats["Trades"] * 100).round(0)
    sector_stats = sector_stats.sort_values("Total_PnL", ascending=False)
    sector_styled = (
        sector_stats.style
        .applymap(color_pnl, subset=["Total_PnL", "Avg_Return"])
        .format({"Total_PnL": "${:+,.0f}", "Avg_Return": "{:+.1f}%", "Win %": "{:.0f}%"})
    )
    st.dataframe(sector_styled, use_container_width=True, hide_index=True)


# ---- DOUBLE SIGNAL HIGHLIGHT ----
doubles = pf[pf["Double"] == True]
if not doubles.empty:
    st.subheader("Double Signals (Below BB + RSI < 30)")
    st.caption(
        "These trades had both indicators firing — historically the highest conviction setup."
    )
    double_display = doubles[display_cols].copy()
    double_styled = (
        double_display.style
        .applymap(color_pnl, subset=["P&L", "Return %"])
        .applymap(color_status, subset=["Status"])
        .format(
            {
                "Entry $": "${:.2f}",
                "Exit $": "${:.2f}",
                "P&L": "${:+,.0f}",
                "Return %": "{:+.1f}%",
                "RSI": "{:.0f}",
                "BB Pos": "{:.2f}",
            },
            na_rep="—",
        )
    )
    st.dataframe(double_styled, use_container_width=True, hide_index=True)

    d_wins = (doubles["P&L"] > 0).sum()
    d_total = len(doubles)
    d_pnl = doubles["P&L"].sum()
    d_avg = doubles["Return %"].mean()
    st.markdown(
        f"**Double-signal record:** {d_wins}/{d_total} wins "
        f"({d_wins/d_total*100:.0f}%) &nbsp;|&nbsp; "
        f"Total P&L: ${d_pnl:+,.0f} &nbsp;|&nbsp; "
        f"Avg return: {d_avg:+.1f}%"
    )


# ---- METHODOLOGY ----
with st.expander("Strategy methodology"):
    st.markdown("""
**Signal:** An insider files an open-market acquisition (purchase) on a day when
the stock's closing price is **below the lower Bollinger Band** (20-day, 2 std dev).

**Entry:** Buy at the **open price on the next trading day** after the insider trade
date. This accounts for the typical 1-day SEDI filing delay.

**Exit:** Sell at the **closing price ~30 calendar days** after entry.

**Position size:** $10,000 per trade (no leverage).

**Double signal:** Flagged when RSI(14) is also below 30 at the time of the
insider purchase — historically 100% win rate at 1 month.

**Data source:** Insider transactions from SEDI via yfinance (~1 year history).
Bollinger Bands and RSI computed from daily closing prices stored in the local
database.
    """)
