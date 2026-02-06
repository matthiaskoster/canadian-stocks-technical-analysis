"""SQLite database layer for storing stock data, indicators, signals, and backtest results."""

import sqlite3
from contextlib import contextmanager

import pandas as pd

from config import DB_PATH

SCHEMA = """
CREATE TABLE IF NOT EXISTS stock_prices (
    ticker TEXT NOT NULL,
    date TEXT NOT NULL,
    open REAL,
    high REAL,
    low REAL,
    close REAL,
    volume INTEGER,
    PRIMARY KEY (ticker, date)
);

CREATE TABLE IF NOT EXISTS indicators (
    ticker TEXT NOT NULL,
    date TEXT NOT NULL,
    ema_5 REAL,
    ema_10 REAL,
    ema_20 REAL,
    ema_50 REAL,
    ema_200 REAL,
    sma_50 REAL,
    sma_200 REAL,
    rsi_14 REAL,
    rsi_21 REAL,
    macd REAL,
    macd_signal REAL,
    macd_histogram REAL,
    vwap_20 REAL,
    PRIMARY KEY (ticker, date)
);

CREATE TABLE IF NOT EXISTS signals (
    ticker TEXT NOT NULL,
    date TEXT NOT NULL,
    signal_type TEXT NOT NULL,
    direction TEXT NOT NULL,
    price REAL,
    strategy TEXT,
    PRIMARY KEY (ticker, date, signal_type)
);

CREATE TABLE IF NOT EXISTS backtest_trades (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ticker TEXT NOT NULL,
    strategy TEXT NOT NULL,
    entry_date TEXT NOT NULL,
    entry_price REAL NOT NULL,
    exit_date TEXT,
    exit_price REAL,
    return_pct REAL,
    direction TEXT NOT NULL DEFAULT 'long'
);

CREATE TABLE IF NOT EXISTS performance_summary (
    ticker TEXT NOT NULL,
    strategy TEXT NOT NULL,
    total_trades INTEGER,
    win_rate REAL,
    avg_gain REAL,
    avg_loss REAL,
    risk_reward REAL,
    max_drawdown REAL,
    total_return REAL,
    buy_hold_return REAL,
    sharpe_ratio REAL,
    PRIMARY KEY (ticker, strategy)
);
"""


@contextmanager
def get_connection():
    """Fresh connection per query for thread safety."""
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA journal_mode=WAL")
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()


def init_db():
    """Create all tables if they don't exist."""
    with get_connection() as conn:
        conn.executescript(SCHEMA)


def store_prices(ticker: str, df: pd.DataFrame):
    """Store OHLCV data. Upserts on (ticker, date)."""
    with get_connection() as conn:
        for date, row in df.iterrows():
            conn.execute(
                "INSERT OR REPLACE INTO stock_prices (ticker, date, open, high, low, close, volume) "
                "VALUES (?, ?, ?, ?, ?, ?, ?)",
                (ticker, date.strftime("%Y-%m-%d"), row["Open"], row["High"],
                 row["Low"], row["Close"], int(row["Volume"])),
            )


def store_indicators(ticker: str, df: pd.DataFrame):
    """Store indicator values. df must have Date index and indicator columns."""
    col_map = {
        "ema_5": "ema_5", "ema_10": "ema_10", "ema_20": "ema_20",
        "ema_50": "ema_50", "ema_200": "ema_200",
        "sma_50": "sma_50", "sma_200": "sma_200",
        "rsi_14": "rsi_14", "rsi_21": "rsi_21",
        "macd": "macd", "macd_signal": "macd_signal", "macd_histogram": "macd_histogram",
        "vwap_20": "vwap_20",
    }
    with get_connection() as conn:
        for date, row in df.iterrows():
            values = {db_col: row.get(src_col) for src_col, db_col in col_map.items()}
            # Convert NaN to None for SQLite
            values = {k: (None if pd.isna(v) else float(v)) for k, v in values.items()}
            conn.execute(
                "INSERT OR REPLACE INTO indicators "
                "(ticker, date, ema_5, ema_10, ema_20, ema_50, ema_200, "
                "sma_50, sma_200, rsi_14, rsi_21, macd, macd_signal, macd_histogram, vwap_20) "
                "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (ticker, date.strftime("%Y-%m-%d"),
                 values["ema_5"], values["ema_10"], values["ema_20"],
                 values["ema_50"], values["ema_200"],
                 values["sma_50"], values["sma_200"],
                 values["rsi_14"], values["rsi_21"],
                 values["macd"], values["macd_signal"], values["macd_histogram"],
                 values["vwap_20"]),
            )


def store_signals(signals: list[dict]):
    """Store signal dicts with keys: ticker, date, signal_type, direction, price, strategy."""
    with get_connection() as conn:
        for s in signals:
            date_str = s["date"].strftime("%Y-%m-%d") if hasattr(s["date"], "strftime") else s["date"]
            conn.execute(
                "INSERT OR REPLACE INTO signals (ticker, date, signal_type, direction, price, strategy) "
                "VALUES (?, ?, ?, ?, ?, ?)",
                (s["ticker"], date_str, s["signal_type"], s["direction"],
                 s.get("price"), s.get("strategy")),
            )


def store_trades(ticker: str, strategy: str, trades: list):
    """Store backtest trades."""
    with get_connection() as conn:
        # Clear old trades for this ticker/strategy
        conn.execute(
            "DELETE FROM backtest_trades WHERE ticker = ? AND strategy = ?",
            (ticker, strategy),
        )
        for t in trades:
            conn.execute(
                "INSERT INTO backtest_trades "
                "(ticker, strategy, entry_date, entry_price, exit_date, exit_price, return_pct, direction) "
                "VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                (ticker, strategy,
                 t.entry_date.strftime("%Y-%m-%d") if hasattr(t.entry_date, "strftime") else t.entry_date,
                 t.entry_price,
                 t.exit_date.strftime("%Y-%m-%d") if t.exit_date and hasattr(t.exit_date, "strftime") else t.exit_date,
                 t.exit_price, t.return_pct, t.direction),
            )


def store_performance(ticker: str, strategy: str, result):
    """Store performance summary from a BacktestResult."""
    with get_connection() as conn:
        conn.execute(
            "INSERT OR REPLACE INTO performance_summary "
            "(ticker, strategy, total_trades, win_rate, avg_gain, avg_loss, "
            "risk_reward, max_drawdown, total_return, buy_hold_return, sharpe_ratio) "
            "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (ticker, strategy, result.total_trades, result.win_rate,
             result.avg_gain, result.avg_loss, result.risk_reward,
             result.max_drawdown, result.total_return, result.buy_hold_return,
             result.sharpe_ratio),
        )


# --- Query methods ---

def get_prices(ticker: str = None) -> pd.DataFrame:
    """Get price data. If ticker is None, get all."""
    with get_connection() as conn:
        if ticker:
            df = pd.read_sql_query(
                "SELECT * FROM stock_prices WHERE ticker = ? ORDER BY date",
                conn, params=(ticker,),
            )
        else:
            df = pd.read_sql_query("SELECT * FROM stock_prices ORDER BY ticker, date", conn)
    if not df.empty:
        df["date"] = pd.to_datetime(df["date"])
    return df


def get_indicators(ticker: str = None) -> pd.DataFrame:
    with get_connection() as conn:
        if ticker:
            df = pd.read_sql_query(
                "SELECT * FROM indicators WHERE ticker = ? ORDER BY date",
                conn, params=(ticker,),
            )
        else:
            df = pd.read_sql_query("SELECT * FROM indicators ORDER BY ticker, date", conn)
    if not df.empty:
        df["date"] = pd.to_datetime(df["date"])
    return df


def get_signals(ticker: str = None, limit: int = None) -> pd.DataFrame:
    with get_connection() as conn:
        query = "SELECT * FROM signals"
        params = []
        if ticker:
            query += " WHERE ticker = ?"
            params.append(ticker)
        query += " ORDER BY date DESC"
        if limit:
            query += " LIMIT ?"
            params.append(limit)
        df = pd.read_sql_query(query, conn, params=params)
    if not df.empty:
        df["date"] = pd.to_datetime(df["date"])
    return df


def get_trades(ticker: str = None, strategy: str = None) -> pd.DataFrame:
    with get_connection() as conn:
        query = "SELECT * FROM backtest_trades WHERE 1=1"
        params = []
        if ticker:
            query += " AND ticker = ?"
            params.append(ticker)
        if strategy:
            query += " AND strategy = ?"
            params.append(strategy)
        query += " ORDER BY entry_date"
        df = pd.read_sql_query(query, conn, params=params)
    if not df.empty:
        df["entry_date"] = pd.to_datetime(df["entry_date"])
        df["exit_date"] = pd.to_datetime(df["exit_date"])
    return df


def get_performance(ticker: str = None, strategy: str = None) -> pd.DataFrame:
    with get_connection() as conn:
        query = "SELECT * FROM performance_summary WHERE 1=1"
        params = []
        if ticker:
            query += " AND ticker = ?"
            params.append(ticker)
        if strategy:
            query += " AND strategy = ?"
            params.append(strategy)
        query += " ORDER BY sharpe_ratio DESC"
        df = pd.read_sql_query(query, conn, params=params)
    return df


def get_latest_prices() -> pd.DataFrame:
    """Get the most recent price row for each ticker."""
    with get_connection() as conn:
        df = pd.read_sql_query(
            "SELECT sp.* FROM stock_prices sp "
            "INNER JOIN (SELECT ticker, MAX(date) as max_date FROM stock_prices GROUP BY ticker) latest "
            "ON sp.ticker = latest.ticker AND sp.date = latest.max_date "
            "ORDER BY sp.ticker",
            conn,
        )
    if not df.empty:
        df["date"] = pd.to_datetime(df["date"])
    return df
