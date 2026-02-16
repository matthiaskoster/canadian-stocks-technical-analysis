"""Entry point for Streamlit dashboard."""

import streamlit as st
from dashboard.components.styles import apply_custom_css

st.set_page_config(
    page_title="Canadian Stocks Technical Analysis",
    page_icon="📈",
    layout="wide",
)

apply_custom_css()

st.title("Canadian Large-Cap Stock Technical Analysis")

# Dashboard navigation cards
col1, col2, col3 = st.columns(3)

with col1:
    st.subheader("Live Signals")
    st.caption("Current indicator readings and recent signals for all 31 stocks")

    st.subheader("Stock Detail")
    st.caption("Deep dive into individual stocks with interactive charts")

    st.subheader("Backtest Results")
    st.caption("Strategy performance across 12 strategies with equity curves")

with col2:
    st.subheader("Sector Analysis")
    st.caption("Performance by sector — Banks, Oil & Gas, Pipelines, Utilities, Tech, Rails, Telecom, Mining")

    st.subheader("Insider Trading")
    st.caption("Insider buy/sell activity across all tracked stocks")

    st.subheader("Commodities")
    st.caption("Gold, silver, copper, oil, natural gas, bitcoin, and uranium with related stock overlays")

with col3:
    st.subheader("News & Calendar")
    st.caption("Latest news and upcoming earnings dates")

    st.subheader("Macro")
    st.caption("WTI crude, USD/CAD, US 10-year yield, and BoC overnight rate")

    st.subheader("Explanations")
    st.caption("Reference guide for all metrics, indicators, and signal types")

st.divider()
st.caption("Navigate using the sidebar. Run `python main.py` to fetch data and generate analysis before using the dashboard.")
