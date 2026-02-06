"""Entry point for Streamlit dashboard."""

import streamlit as st

st.set_page_config(
    page_title="Canadian Stocks Technical Analysis",
    page_icon="📈",
    layout="wide",
)

st.title("Canadian Large-Cap Stock Technical Analysis")
st.markdown("Use the sidebar to navigate between pages.")
