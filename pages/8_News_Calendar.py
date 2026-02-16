"""Page 8: News & Earnings Calendar — Recent headlines and upcoming earnings dates."""

import streamlit as st
import pandas as pd

from data.database import get_news, get_earnings, init_db
from dashboard.components.styles import apply_custom_css
from config import ALL_STOCKS, SECTORS

st.set_page_config(page_title="News & Calendar", page_icon="📰", layout="wide")
apply_custom_css()
st.title("News & Earnings Calendar")

init_db()


@st.cache_data(ttl=300)
def load_news():
    return get_news()


@st.cache_data(ttl=300)
def load_earnings():
    return get_earnings()


# --- Earnings Calendar ---
st.subheader("Upcoming Earnings Dates")

earnings_df = load_earnings()

if not earnings_df.empty:
    earnings_display = earnings_df.copy()
    earnings_display["Name"] = earnings_display["ticker"].map(ALL_STOCKS)
    earnings_display["Sector"] = earnings_display["ticker"].map(SECTORS)
    earnings_display = earnings_display.rename(columns={
        "ticker": "Ticker", "earnings_date": "Earnings Date",
    })
    earnings_display = earnings_display[["Ticker", "Name", "Sector", "Earnings Date"]]
    earnings_display = earnings_display.sort_values("Earnings Date")

    # Drop earnings more than 5 days before today
    today = pd.Timestamp.now().normalize()
    cutoff = today - pd.Timedelta(days=5)
    earnings_display = earnings_display[
        pd.to_datetime(earnings_display["Earnings Date"]) >= cutoff
    ]

    # Highlight dates in the next 14 days
    two_weeks = today + pd.Timedelta(days=14)

    def style_upcoming(val):
        try:
            d = pd.to_datetime(val)
            if d <= two_weeks:
                return "color: #ff9800; font-weight: bold"
        except Exception:
            pass
        return ""

    styled = earnings_display.style.applymap(style_upcoming, subset=["Earnings Date"])
    st.dataframe(styled, use_container_width=True, hide_index=True)
else:
    st.info("No earnings data. Run `python3 main.py` to fetch.")

# --- News ---
st.subheader("Recent News")

news_df = load_news()

if not news_df.empty:
    # Filters
    col1, col2 = st.columns(2)
    with col1:
        sector_options = ["All"] + sorted(set(SECTORS.values()))
        sector_filter = st.selectbox("Sector", sector_options)
    with col2:
        if sector_filter == "All":
            available = sorted(news_df["ticker"].unique())
        else:
            sector_tickers = [t for t, s in SECTORS.items() if s == sector_filter]
            available = sorted([t for t in news_df["ticker"].unique() if t in sector_tickers])
        ticker_options = ["All stocks"] + available
        ticker_filter = st.selectbox("Ticker", ticker_options)

    filtered = news_df.copy()
    if sector_filter != "All":
        sector_tickers = [t for t, s in SECTORS.items() if s == sector_filter]
        filtered = filtered[filtered["ticker"].isin(sector_tickers)]
    if ticker_filter != "All stocks":
        filtered = filtered[filtered["ticker"] == ticker_filter]

    # Display as a table with clickable links
    if not filtered.empty:
        display = filtered[["ticker", "published", "title", "source", "link"]].copy()
        display["Name"] = display["ticker"].map(ALL_STOCKS)
        display = display[["ticker", "Name", "published", "title", "source", "link"]]
        display.columns = ["Ticker", "Name", "Published", "Title", "Source", "Link"]

        # Show as markdown cards for better readability
        for _, row in display.head(50).iterrows():
            link_text = f"[{row['Title']}]({row['Link']})" if row["Link"] else row["Title"]
            source_tag = f" — *{row['Source']}*" if row["Source"] else ""
            st.markdown(
                f"**{row['Ticker']}** | {row['Published']}{source_tag}  \n"
                f"{link_text}"
            )
        if len(display) > 50:
            st.caption(f"Showing 50 of {len(display)} articles.")
    else:
        st.info("No news matches the current filters.")
else:
    st.info("No news data. Run `python3 main.py` to fetch.")
