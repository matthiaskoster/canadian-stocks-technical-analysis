"""Shared CSS styling for the Streamlit dashboard."""

import streamlit as st


def apply_custom_css():
    """Inject custom CSS for a cohesive light-themed financial dashboard."""
    st.markdown("""
    <style>
    /* --- Metric cards --- */
    div[data-testid="stMetric"] {
        background: #f5f7fa;
        border: 1px solid #e0e0e0;
        border-radius: 8px;
        padding: 12px 16px;
    }

    /* --- Subheader accent line --- */
    div[data-testid="stSubheader"] {
        border-bottom: 2px solid #2196f3;
        padding-bottom: 6px;
        margin-bottom: 8px;
    }

    /* --- DataFrames --- */
    div[data-testid="stDataFrame"] th {
        background-color: rgba(33, 150, 243, 0.08) !important;
    }

    /* --- Sidebar refinement --- */
    section[data-testid="stSidebar"] {
        border-right: 1px solid #e0e0e0;
    }

    /* --- Radio buttons / filter chips --- */
    div[data-testid="stRadio"] label {
        border-radius: 16px;
    }

    /* --- Tighter section spacing --- */
    div[data-testid="stVerticalBlock"] > div {
        margin-bottom: 0.25rem;
    }

    /* --- Expander styling --- */
    details[data-testid="stExpander"] {
        border: 1px solid #e0e0e0;
        border-radius: 8px;
    }
    </style>
    """, unsafe_allow_html=True)
