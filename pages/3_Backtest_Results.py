"""Page 3: Backtest Results — Strategy comparison and equity curves."""

import streamlit as st
import pandas as pd

from data.database import get_performance, get_trades, init_db
from dashboard.components.charts import create_equity_curve
from dashboard.components.tables import style_return, format_pct
from config import ALL_STOCKS, TICKERS

st.set_page_config(page_title="Backtest Results", page_icon="📈", layout="wide")
st.title("Backtest Results")

init_db()


@st.cache_data(ttl=300)
def load_backtest_data():
    perf = get_performance()
    return perf


perf = load_backtest_data()

if perf.empty:
    st.warning("No backtest results. Run `python main.py` first.")
    st.stop()

# Filters
col1, col2 = st.columns(2)
with col1:
    strategies = sorted(perf["strategy"].unique())
    selected_strategies = st.multiselect("Strategies", strategies, default=strategies)
with col2:
    tickers = sorted(perf["ticker"].unique())
    selected_tickers = st.multiselect("Tickers", tickers, default=tickers,
                                       format_func=lambda t: f"{t} — {ALL_STOCKS.get(t, '')}")

filtered = perf[perf["strategy"].isin(selected_strategies) & perf["ticker"].isin(selected_tickers)]

# Strategy rankings by Sharpe ratio
st.subheader("Strategy Rankings (by average Sharpe ratio)")

strategy_summary = filtered.groupby("strategy").agg({
    "sharpe_ratio": "mean",
    "total_return": "mean",
    "win_rate": "mean",
    "max_drawdown": "mean",
    "total_trades": "sum",
}).round(2).sort_values("sharpe_ratio", ascending=False)

strategy_summary.columns = ["Avg Sharpe", "Avg Return %", "Avg Win Rate %", "Avg Max DD %", "Total Trades"]
st.dataframe(strategy_summary, use_container_width=True)

# Detailed performance table
st.subheader("Detailed Performance")

display_cols = ["ticker", "strategy", "total_trades", "win_rate", "avg_gain",
                "avg_loss", "risk_reward", "max_drawdown", "total_return",
                "buy_hold_return", "sharpe_ratio"]
detail = filtered[display_cols].copy()
detail.columns = ["Ticker", "Strategy", "Trades", "Win Rate %", "Avg Gain %",
                   "Avg Loss %", "Risk/Reward", "Max DD %", "Strategy Return %",
                   "Buy & Hold %", "Sharpe"]

styled = detail.style.applymap(
    style_return, subset=["Strategy Return %", "Buy & Hold %", "Max DD %"]
).format({
    "Win Rate %": "{:.1f}%",
    "Avg Gain %": "{:+.2f}%",
    "Avg Loss %": "{:+.2f}%",
    "Risk/Reward": "{:.2f}",
    "Max DD %": "{:.2f}%",
    "Strategy Return %": "{:+.2f}%",
    "Buy & Hold %": "{:+.2f}%",
    "Sharpe": "{:.2f}",
}, na_rep="—")

st.dataframe(styled, use_container_width=True, hide_index=True, height=500)

# Win rate visualization
st.subheader("Win Rate by Strategy")
import plotly.graph_objects as go

if not filtered.empty:
    wr_by_strategy = filtered.groupby("strategy")["win_rate"].mean().sort_values(ascending=True)

    fig_wr = go.Figure(go.Bar(
        x=wr_by_strategy.values,
        y=wr_by_strategy.index,
        orientation="h",
        marker_color=["#26a69a" if v >= 50 else "#ef5350" for v in wr_by_strategy.values],
        text=[f"{v:.1f}%" for v in wr_by_strategy.values],
        textposition="auto",
    ))
    fig_wr.add_vline(x=50, line_dash="dash", line_color="gray", opacity=0.5)
    fig_wr.update_layout(
        title="Average Win Rate by Strategy", height=300, template="plotly_dark",
        xaxis_title="Win Rate %", margin=dict(l=120, r=20, t=40, b=30),
    )
    st.plotly_chart(fig_wr, use_container_width=True)

# Equity curve for selected ticker/strategy
st.subheader("Equity Curve")
col_t, col_s = st.columns(2)
with col_t:
    eq_ticker = st.selectbox("Ticker", sorted(perf["ticker"].unique()), key="eq_ticker",
                              format_func=lambda t: f"{t} — {ALL_STOCKS.get(t, '')}")
with col_s:
    eq_strategy = st.selectbox("Strategy", sorted(perf["strategy"].unique()), key="eq_strat")


@st.cache_data(ttl=300)
def load_trades(ticker, strategy):
    return get_trades(ticker, strategy)


trades = load_trades(eq_ticker, eq_strategy)
fig_eq = create_equity_curve(trades, height=350)
st.plotly_chart(fig_eq, use_container_width=True)

if not trades.empty:
    st.caption(f"{len(trades)} trades for {eq_ticker} using {eq_strategy}")
