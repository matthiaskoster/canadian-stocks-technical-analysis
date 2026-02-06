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

- **Live Signals** — Current indicator readings and recent signals for all 25 stocks
- **Stock Detail** — Deep dive into individual stocks with interactive charts
- **Backtest Results** — Strategy performance comparison and equity curves
- **Sector Analysis** — Sector groupings, comparative performance, and correlations
""")

st.divider()
st.caption("Run `python main.py` to fetch data and generate analysis before using the dashboard.")
