"""Fetch historical stock data from Yahoo Finance."""

import warnings
from datetime import datetime, timedelta

import pandas as pd
import yfinance as yf

from config import FETCH_DAYS


def fetch_stock_data(ticker: str, days: int = FETCH_DAYS, start_date: str | None = None) -> pd.DataFrame | None:
    """Fetch historical daily OHLCV data for a single ticker.

    Args:
        start_date: Optional ISO date string (YYYY-MM-DD) to fetch from instead of days ago.

    Returns DataFrame with columns: Open, High, Low, Close, Volume
    indexed by naive date. Returns None if fetch fails.
    """
    end = datetime.now() + timedelta(days=1)  # yfinance end date is exclusive
    start = datetime.fromisoformat(start_date) if start_date else end - timedelta(days=days + 1)

    try:
        stock = yf.Ticker(ticker)
        df = stock.history(start=start.strftime("%Y-%m-%d"), end=end.strftime("%Y-%m-%d"))

        if df.empty:
            warnings.warn(f"No data returned for {ticker}")
            return None

        # Normalize timezone-aware index to naive dates
        if df.index.tz is not None:
            df.index = df.index.tz_localize(None)
        df.index = pd.to_datetime(df.index).normalize()
        df.index.name = "Date"

        # Keep only OHLCV columns
        cols = ["Open", "High", "Low", "Close", "Volume"]
        df = df[[c for c in cols if c in df.columns]]

        # Validate no negative prices
        price_cols = [c for c in ["Open", "High", "Low", "Close"] if c in df.columns]
        if (df[price_cols] < 0).any().any():
            warnings.warn(f"Negative prices found for {ticker}, dropping those rows")
            mask = (df[price_cols] >= 0).all(axis=1)
            df = df[mask]

        # Drop rows with NaN in critical columns
        df = df.dropna(subset=price_cols)

        if df.empty:
            warnings.warn(f"No valid data after cleaning for {ticker}")
            return None

        return df

    except Exception as e:
        warnings.warn(f"Failed to fetch {ticker}: {e}")
        return None


def fetch_usdcad_rate() -> float | None:
    """Fetch the current USD/CAD exchange rate (CAD per 1 USD).

    Returns the latest close, or None if fetch fails.
    """
    try:
        fx = yf.Ticker("USDCAD=X")
        hist = fx.history(period="5d")
        if hist.empty:
            return None
        return float(hist["Close"].iloc[-1])
    except Exception as e:
        warnings.warn(f"Failed to fetch USD/CAD rate: {e}")
        return None


def fetch_insider_trades(ticker: str) -> pd.DataFrame | None:
    """Fetch insider transaction data for a single ticker.

    Returns DataFrame with insider trade columns, or None if unavailable.
    """
    try:
        stock = yf.Ticker(ticker)
        df = stock.insider_transactions
        if df is None or df.empty:
            return None
        return df
    except Exception as e:
        warnings.warn(f"Failed to fetch insider trades for {ticker}: {e}")
        return None


def fetch_news(ticker: str) -> list[dict] | None:
    """Fetch recent news for a ticker from yfinance.

    Returns list of dicts with: title, published, link, source.
    """
    try:
        stock = yf.Ticker(ticker)
        news = stock.news
        if not news:
            return None
        articles = []
        for item in news:
            content = item.get("content", item) if isinstance(item, dict) else item
            title = content.get("title", "")
            if not title:
                continue
            pub_date = content.get("pubDate", content.get("providerPublishTime", ""))
            if isinstance(pub_date, (int, float)):
                pub_date = datetime.fromtimestamp(pub_date).strftime("%Y-%m-%d %H:%M")
            link = content.get("canonicalUrl", content.get("link", ""))
            if isinstance(link, dict):
                link = link.get("url", "")
            source = content.get("provider", content.get("source", ""))
            if isinstance(source, dict):
                source = source.get("displayName", source.get("name", ""))
            articles.append({
                "title": title[:500],
                "published": str(pub_date)[:20] if pub_date else "",
                "link": str(link),
                "source": str(source),
            })
        return articles if articles else None
    except Exception as e:
        warnings.warn(f"Failed to fetch news for {ticker}: {e}")
        return None


def fetch_earnings_date(ticker: str) -> str | None:
    """Fetch next earnings date for a ticker from yfinance.

    Returns ISO date string or None.
    """
    try:
        stock = yf.Ticker(ticker)
        cal = stock.calendar
        if cal is None:
            return None
        # cal can be a dict or DataFrame depending on yfinance version
        if isinstance(cal, dict):
            dates = cal.get("Earnings Date", [])
            if dates:
                d = dates[0]
                return d.strftime("%Y-%m-%d") if hasattr(d, "strftime") else str(d)[:10]
        elif isinstance(cal, pd.DataFrame) and not cal.empty:
            if "Earnings Date" in cal.index:
                val = cal.loc["Earnings Date"].iloc[0]
                return val.strftime("%Y-%m-%d") if hasattr(val, "strftime") else str(val)[:10]
        return None
    except Exception as e:
        warnings.warn(f"Failed to fetch earnings date for {ticker}: {e}")
        return None


def fetch_fred_series(series_id: str, api_key: str, start_date: str = None) -> pd.DataFrame | None:
    """Fetch a FRED time series. Returns DataFrame with date index and value column.

    If start_date is provided (YYYY-MM-DD), only fetches observations from that date onward.
    """
    try:
        from fredapi import Fred
        fred = Fred(api_key=api_key)
        s = fred.get_series(series_id, observation_start=start_date)
        if s is None or s.empty:
            return None
        df = s.to_frame(name="value")
        df.index.name = "date"
        df = df.dropna()
        return df
    except ImportError:
        warnings.warn("fredapi not installed. Run: pip install fredapi")
        return None
    except Exception as e:
        warnings.warn(f"Failed to fetch FRED series {series_id}: {e}")
        return None


def fetch_boc_rate(start_date: str = None) -> pd.DataFrame | None:
    """Fetch Bank of Canada overnight rate from the BoC Valet API.

    If start_date is provided (YYYY-MM-DD), only fetches observations from that date onward.
    Otherwise fetches the last 260 observations.
    """
    import urllib.request
    import json

    if start_date:
        url = f"https://www.bankofcanada.ca/valet/observations/V39079/json?start_date={start_date}"
    else:
        url = "https://www.bankofcanada.ca/valet/observations/V39079/json?recent=260"
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "DMAtracker/1.0"})
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read().decode())
        observations = data.get("observations", [])
        if not observations:
            return None
        rows = []
        for obs in observations:
            date_str = obs.get("d", "")
            val = obs.get("V39079", {}).get("v")
            if date_str and val:
                rows.append({"date": date_str, "value": float(val)})
        if not rows:
            return None
        df = pd.DataFrame(rows)
        df["date"] = pd.to_datetime(df["date"])
        return df
    except Exception as e:
        warnings.warn(f"Failed to fetch BoC rate: {e}")
        return None


def fetch_all_stocks(tickers: list[str]) -> dict[str, pd.DataFrame]:
    """Fetch data for all tickers. Returns dict of ticker -> DataFrame."""
    results = {}
    for ticker in tickers:
        print(f"  Fetching {ticker}...")
        df = fetch_stock_data(ticker)
        if df is not None:
            results[ticker] = df
            print(f"    Got {len(df)} rows for {ticker}")
        else:
            print(f"    SKIPPED {ticker} (no data)")
    return results
