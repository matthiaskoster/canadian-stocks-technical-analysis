"""Entry point for Streamlit dashboard."""

import streamlit as st

st.set_page_config(
    page_title="Canadian Stocks Technical Analysis",
    page_icon="📈",
    layout="wide",
)

st.title("Canadian Large-Cap Stock Technical Analysis")
st.markdown("""
Navigate using the sidebar:

- **Live Signals** — Current indicator readings and recent signals for all 31 stocks
- **Stock Detail** — Deep dive into individual stocks with interactive charts
- **Backtest Results** — Strategy performance across 11 strategies with equity curves
- **Sector Analysis** — Performance by sector (Banks, Oil & Gas, Pipelines, Utilities, Tech, Rails, Telecom, Mining)
- **Explanations** — Reference guide for all metrics, indicators, and signal types
- **Insider Trading** — Insider buy/sell activity across all tracked stocks
- **Commodities** — Gold, silver, copper, oil, natural gas, bitcoin, and uranium with related stock overlays
- **News & Calendar** — Latest news and upcoming earnings dates
- **Macro** — WTI crude, USD/CAD, US 10-year yield, and BoC overnight rate
""")

st.divider()
st.caption("Run `python main.py` to fetch data and generate analysis before using the dashboard.")
