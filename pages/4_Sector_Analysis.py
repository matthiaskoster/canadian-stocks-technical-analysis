"""Page 4: Sector Analysis — Sector grouping, comparative performance, and correlations."""

import streamlit as st
import pandas as pd

from data.database import get_performance, get_prices, init_db
from dashboard.components.charts import (
    create_sector_comparison, create_correlation_heatmap,
)
from dashboard.components.tables import style_return
from config import SECTORS, ALL_STOCKS, SECTOR_GROUPS, SECTOR_NAMES

st.set_page_config(page_title="Sector Analysis", page_icon="📈", layout="wide")
st.title("Sector Analysis")

init_db()


@st.cache_data(ttl=300)
def load_sector_data():
    perf = get_performance()
    prices = get_prices()
    return perf, prices


perf, all_prices = load_sector_data()

if perf.empty:
    st.warning("No performance data. Run `python main.py` first.")
    st.stop()

# Sector comparison charts
st.subheader("Sector Performance Comparison")

metric = st.selectbox("Metric", [
    "total_return", "win_rate", "sharpe_ratio", "max_drawdown",
], format_func=lambda m: m.replace("_", " ").title())

strategy_filter = st.selectbox("Strategy", ["All"] + sorted(perf["strategy"].unique()))
if strategy_filter != "All":
    perf_filtered = perf[perf["strategy"] == strategy_filter]
else:
    perf_filtered = perf

fig_sector = create_sector_comparison(perf_filtered, metric=metric)
st.plotly_chart(fig_sector, use_container_width=True)

# Sector breakdown tables
st.subheader("Sector Breakdown")

tabs = st.tabs(SECTOR_NAMES)

for tab, (sector_name, sector_dict) in zip(tabs, SECTOR_GROUPS):
    with tab:
        sector_perf = perf_filtered[perf_filtered["ticker"].isin(sector_dict.keys())]
        if sector_perf.empty:
            st.info(f"No data for {sector_name}")
            continue

        # Average by ticker across strategies
        ticker_avg = sector_perf.groupby("ticker").agg({
            "total_return": "mean",
            "win_rate": "mean",
            "sharpe_ratio": "mean",
            "max_drawdown": "mean",
            "buy_hold_return": "first",
        }).round(2)

        ticker_avg["name"] = ticker_avg.index.map(ALL_STOCKS)
        ticker_avg = ticker_avg[["name", "total_return", "buy_hold_return", "win_rate", "sharpe_ratio", "max_drawdown"]]
        ticker_avg.columns = ["Name", "Avg Strategy Return %", "Buy & Hold %", "Avg Win Rate %", "Avg Sharpe", "Avg Max DD %"]
        ticker_avg = ticker_avg.sort_values("Avg Sharpe", ascending=False)

        styled = ticker_avg.style.applymap(
            style_return, subset=["Avg Strategy Return %", "Buy & Hold %", "Avg Max DD %"]
        ).format({
            "Avg Strategy Return %": "{:+.2f}%",
            "Buy & Hold %": "{:+.2f}%",
            "Avg Win Rate %": "{:.1f}%",
            "Avg Sharpe": "{:.2f}",
            "Avg Max DD %": "{:.2f}%",
        }, na_rep="—")
        st.dataframe(styled, use_container_width=True)

# Correlation matrix
st.subheader("Return Correlation Matrix")

sector_corr = st.radio("Sector", ["All"] + SECTOR_NAMES, horizontal=True, key="corr_sector")

sector_map = {name: d for name, d in SECTOR_GROUPS}
sector_map["All"] = ALL_STOCKS
corr_tickers = list(sector_map[sector_corr].keys())

if not all_prices.empty:
    prices_dict = {}
    for ticker in corr_tickers:
        tk_prices = all_prices[all_prices["ticker"] == ticker].set_index("date")["close"]
        if not tk_prices.empty:
            prices_dict[ticker] = tk_prices

    if prices_dict:
        fig_corr = create_correlation_heatmap(prices_dict, height=max(400, len(prices_dict) * 25))
        st.plotly_chart(fig_corr, use_container_width=True)
    else:
        st.info("No price data available for correlation analysis.")
else:
    st.info("No price data. Run `python main.py` first.")

# Strategy insights by sector
st.subheader("Best Strategy by Sector")

if not perf.empty:
    best = perf.copy()
    best["sector"] = best["ticker"].map(SECTORS)
    best_by_sector = best.groupby(["sector", "strategy"])["sharpe_ratio"].mean().reset_index()
    best_by_sector = best_by_sector.sort_values(["sector", "sharpe_ratio"], ascending=[True, False])
    top_per_sector = best_by_sector.groupby("sector").head(3)
    top_per_sector.columns = ["Sector", "Strategy", "Avg Sharpe Ratio"]
    top_per_sector["Avg Sharpe Ratio"] = top_per_sector["Avg Sharpe Ratio"].round(2)
    st.dataframe(top_per_sector, use_container_width=True, hide_index=True)
