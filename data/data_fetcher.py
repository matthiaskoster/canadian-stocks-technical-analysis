"""Fetch historical stock data from Yahoo Finance."""

import warnings
from datetime import datetime, timedelta

import pandas as pd
import yfinance as yf

from config import FETCH_DAYS


def fetch_stock_data(ticker: str, days: int = FETCH_DAYS) -> pd.DataFrame | None:
    """Fetch historical daily OHLCV data for a single ticker.

    Returns DataFrame with columns: Open, High, Low, Close, Volume
    indexed by naive date. Returns None if fetch fails.
    """
    end = datetime.now()
    start = end - timedelta(days=days)

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
