"""Main orchestration script for Canadian stock technical analysis."""

import argparse
import time
from datetime import date, timedelta

from config import TICKERS, ALL_STOCKS, COMMODITY_TICKERS, COMMODITIES, FRED_SERIES
from data.data_fetcher import (
    fetch_stock_data, fetch_all_stocks, fetch_insider_trades,
    fetch_news, fetch_earnings_date, fetch_fred_series, fetch_boc_rate,
)
from data.database import (
    init_db, store_prices, store_indicators, store_signals,
    store_trades, store_performance, get_prices, store_insider_trades,
    get_last_fetch, log_fetch, store_news, store_earnings, store_macro,
)
from indicators import calculate_all_indicators
from strategies import detect_all_signals, BACKTEST_STRATEGIES
from backtesting.backtest_engine import BacktestEngine
import pandas as pd


def run_pipeline(tickers: list[str], fetch: bool = True, force: bool = False):
    """Run the full analysis pipeline for given tickers."""
    init_db()
    engine = BacktestEngine()
    today = date.today().isoformat()

    # Step 1: Fetch data
    if fetch:
        print("=" * 60)
        print("FETCHING DATA")
        print("=" * 60)

        fetched_count = 0
        for ticker in tickers:
            last = get_last_fetch(ticker, "prices")
            if last == today and not force:
                print(f"  {ticker}: prices up to date (last fetch: {last})")
                continue

            # Incremental: fetch from day after last fetch, or full history
            start_date = None
            if last and not force:
                start_date = (date.fromisoformat(last) + timedelta(days=1)).isoformat()
                print(f"  {ticker}: fetching prices from {start_date}...")
            else:
                print(f"  {ticker}: fetching full price history...")

            df = fetch_stock_data(ticker, start_date=start_date)
            if df is not None:
                store_prices(ticker, df)
                log_fetch(ticker, "prices")
                fetched_count += 1
                print(f"    Got {len(df)} rows")
            else:
                if start_date:
                    # No new rows but fetch succeeded (market closed, etc.)
                    log_fetch(ticker, "prices")
                print(f"    No new data")

        print(f"\nFetched prices for {fetched_count}/{len(tickers)} stocks")

        # Fetch insider trades
        print("\nFetching insider trades...")
        for ticker in tickers:
            last = get_last_fetch(ticker, "insider")
            if last == today and not force:
                print(f"  {ticker}: insider data up to date (last fetch: {last})")
                continue

            print(f"  {ticker}: fetching insider trades...")
            insider_df = fetch_insider_trades(ticker)
            if insider_df is not None and not insider_df.empty:
                store_insider_trades(ticker, insider_df)
                print(f"    {len(insider_df)} insider trades")
            else:
                print(f"    no insider data")
            log_fetch(ticker, "insider")
        print("Insider trades done.")

        # Fetch commodity prices (reuses same stock_prices table)
        print("\nFetching commodity prices...")
        commodity_count = 0
        for ticker in COMMODITY_TICKERS:
            last = get_last_fetch(ticker, "prices")
            if last == today and not force:
                print(f"  {ticker} ({COMMODITIES[ticker]}): up to date")
                continue

            start_date = None
            if last and not force:
                start_date = (date.fromisoformat(last) + timedelta(days=1)).isoformat()
                print(f"  {ticker} ({COMMODITIES[ticker]}): fetching from {start_date}...")
            else:
                print(f"  {ticker} ({COMMODITIES[ticker]}): fetching full history...")

            df = fetch_stock_data(ticker, start_date=start_date)
            if df is not None:
                store_prices(ticker, df)
                log_fetch(ticker, "prices")
                commodity_count += 1
                print(f"    Got {len(df)} rows")
            else:
                if start_date:
                    log_fetch(ticker, "prices")
                print(f"    No new data")

        print(f"Fetched prices for {commodity_count}/{len(COMMODITY_TICKERS)} commodities")

        # Fetch news and earnings calendar
        print("\nFetching news & earnings calendar...")
        news_count = 0
        for ticker in tickers:
            last = get_last_fetch(ticker, "news")
            if last == today and not force:
                continue
            articles = fetch_news(ticker)
            if articles:
                store_news(ticker, articles)
                news_count += len(articles)
            earnings = fetch_earnings_date(ticker)
            if earnings:
                store_earnings(ticker, earnings)
            log_fetch(ticker, "news")
        print(f"  {news_count} news articles across {len(tickers)} stocks")

        # Fetch macro data (FRED + BoC)
        print("\nFetching macro data...")
        import os
        from dotenv import load_dotenv
        env_path = os.path.join(os.path.dirname(__file__), ".env.local")
        if os.path.exists(env_path):
            load_dotenv(env_path)
        fred_key = os.environ.get("FRED_API")
        if fred_key:
            for series_id, name in FRED_SERIES.items():
                last = get_last_fetch(series_id, "macro")
                if last == today and not force:
                    print(f"  {name}: up to date")
                    continue
                print(f"  {name}: fetching from FRED...")
                df = fetch_fred_series(series_id, fred_key)
                if df is not None:
                    store_macro(series_id, df)
                    log_fetch(series_id, "macro")
                    print(f"    {len(df)} data points")
                else:
                    print(f"    no data")
        else:
            print("  FRED_API key not found in .env.local, skipping FRED series")

        # Bank of Canada overnight rate
        last = get_last_fetch("BOC_OVERNIGHT", "macro")
        if last != today or force:
            print("  BoC overnight rate: fetching...")
            boc_df = fetch_boc_rate()
            if boc_df is not None:
                store_macro("BOC_OVERNIGHT", boc_df)
                log_fetch("BOC_OVERNIGHT", "macro")
                print(f"    {len(boc_df)} data points")
            else:
                print(f"    no data")
        else:
            print("  BoC overnight rate: up to date")
        print("Macro data done.")
    else:
        print("Skipping data fetch (--no-fetch)")

    # Step 2: Calculate indicators and detect signals
    print("\n" + "=" * 60)
    print("CALCULATING INDICATORS & DETECTING SIGNALS")
    print("=" * 60)

    for ticker in tickers:
        prices_df = get_prices(ticker)
        if prices_df.empty:
            print(f"  {ticker}: No price data, skipping")
            continue

        # Reconstruct OHLCV DataFrame with date index
        prices_df = prices_df.set_index("date")
        prices_df.columns = [c.capitalize() if c != "volume" else "Volume"
                             for c in prices_df.columns]
        # Rename columns to match expected format
        rename_map = {"Ticker": "Ticker", "Open": "Open", "High": "High",
                      "Low": "Low", "Close": "Close", "Volume": "Volume"}
        for old, new in rename_map.items():
            if old.lower() in [c.lower() for c in prices_df.columns]:
                pass  # columns already correct after capitalize

        # Drop ticker column if present
        if "Ticker" in prices_df.columns:
            prices_df = prices_df.drop(columns=["Ticker"])

        # Calculate indicators
        ind_df = calculate_all_indicators(prices_df)
        store_indicators(ticker, ind_df)

        # Detect signals
        signals = detect_all_signals(ind_df, ticker)
        if signals:
            store_signals(signals)
        print(f"  {ticker}: {len(ind_df)} rows, {len(signals)} signals")

        # Step 3: Backtest all strategies
        for strategy_name, (entry_func, exit_func) in BACKTEST_STRATEGIES.items():
            try:
                entry_signals = entry_func(ind_df)
                exit_signals = exit_func(ind_df)
                result = engine.run(ind_df, entry_signals, exit_signals, ticker, strategy_name)
                store_trades(ticker, strategy_name, result.trades)
                store_performance(ticker, strategy_name, result)
            except Exception as e:
                print(f"    Backtest error ({strategy_name}): {e}")

    print("\nPipeline complete.")


def main():
    parser = argparse.ArgumentParser(
        description="Canadian Large-Cap Stock Technical Analysis"
    )
    parser.add_argument("--fetch-only", action="store_true", help="Only fetch data, no analysis")
    parser.add_argument("--no-fetch", action="store_true", help="Skip data fetching, use cached")
    parser.add_argument("--force", action="store_true", help="Force re-fetch even if data is current")
    parser.add_argument("--ticker", type=str, help="Run for a single ticker (e.g. RY.TO)")
    args = parser.parse_args()

    start = time.time()

    if args.ticker:
        tickers = [args.ticker]
    else:
        tickers = TICKERS

    if args.fetch_only:
        init_db()
        print("Fetching data only...")
        stock_data = fetch_all_stocks(tickers)
        for ticker, df in stock_data.items():
            store_prices(ticker, df)
        print(f"Fetched and stored {len(stock_data)} stocks.")
    else:
        run_pipeline(tickers, fetch=not args.no_fetch, force=args.force)

    elapsed = time.time() - start
    print(f"\nTotal time: {elapsed:.1f}s")


if __name__ == "__main__":
    main()
