"""Main orchestration script for Canadian stock technical analysis."""

import argparse
import time

from config import TICKERS, ALL_STOCKS
from data.data_fetcher import fetch_stock_data, fetch_all_stocks
from data.database import (
    init_db, store_prices, store_indicators, store_signals,
    store_trades, store_performance, get_prices,
)
from indicators import calculate_all_indicators
from strategies import detect_all_signals, BACKTEST_STRATEGIES
from backtesting.backtest_engine import BacktestEngine
import pandas as pd


def run_pipeline(tickers: list[str], fetch: bool = True):
    """Run the full analysis pipeline for given tickers."""
    init_db()
    engine = BacktestEngine()

    # Step 1: Fetch data
    if fetch:
        print("=" * 60)
        print("FETCHING DATA")
        print("=" * 60)
        stock_data = fetch_all_stocks(tickers)
        print(f"\nFetched data for {len(stock_data)}/{len(tickers)} stocks")

        # Store prices
        for ticker, df in stock_data.items():
            store_prices(ticker, df)
        print("Prices stored to database.")
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
        run_pipeline(tickers, fetch=not args.no_fetch)

    elapsed = time.time() - start
    print(f"\nTotal time: {elapsed:.1f}s")


if __name__ == "__main__":
    main()
