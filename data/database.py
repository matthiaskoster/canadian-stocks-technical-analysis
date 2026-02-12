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
    atr_14 REAL,
    bb_upper REAL,
    bb_middle REAL,
    bb_lower REAL,
    bb_width REAL,
    adx_14 REAL,
    plus_di REAL,
    minus_di REAL,
    obv REAL,
    stoch_k REAL,
    stoch_d REAL,
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

CREATE TABLE IF NOT EXISTS insider_trades (
    ticker TEXT NOT NULL,
    date TEXT NOT NULL,
    insider TEXT,
    position TEXT,
    transaction_type TEXT,
    shares INTEGER,
    value REAL,
    ownership TEXT,
    PRIMARY KEY (ticker, date, insider, transaction_type)
);

CREATE TABLE IF NOT EXISTS fetch_log (
    ticker TEXT NOT NULL,
    data_type TEXT NOT NULL,
    last_fetch TEXT NOT NULL,
    PRIMARY KEY (ticker, data_type)
);

CREATE TABLE IF NOT EXISTS stock_news (
    ticker TEXT NOT NULL,
    published TEXT NOT NULL,
    title TEXT NOT NULL,
    link TEXT,
    source TEXT,
    PRIMARY KEY (ticker, title)
);

CREATE TABLE IF NOT EXISTS earnings_calendar (
    ticker TEXT NOT NULL,
    earnings_date TEXT,
    PRIMARY KEY (ticker)
);

CREATE TABLE IF NOT EXISTS macro_data (
    series_id TEXT NOT NULL,
    date TEXT NOT NULL,
    value REAL,
    PRIMARY KEY (series_id, date)
);
"""

# New indicator columns added after initial schema
_INDICATOR_MIGRATIONS = [
    "atr_14 REAL", "bb_upper REAL", "bb_middle REAL", "bb_lower REAL",
    "bb_width REAL", "adx_14 REAL", "plus_di REAL", "minus_di REAL",
    "obv REAL", "stoch_k REAL", "stoch_d REAL",
]


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
    """Create all tables if they don't exist, and migrate existing ones."""
    with get_connection() as conn:
        conn.executescript(SCHEMA)
        # Migrate existing indicators table: add new columns if missing
        for col_def in _INDICATOR_MIGRATIONS:
            try:
                conn.execute(f"ALTER TABLE indicators ADD COLUMN {col_def}")
            except sqlite3.OperationalError:
                pass  # column already exists


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
        "atr_14": "atr_14",
        "bb_upper": "bb_upper", "bb_middle": "bb_middle",
        "bb_lower": "bb_lower", "bb_width": "bb_width",
        "adx_14": "adx_14", "plus_di": "plus_di", "minus_di": "minus_di",
        "obv": "obv",
        "stoch_k": "stoch_k", "stoch_d": "stoch_d",
    }
    columns = list(col_map.values())
    placeholders = ", ".join(["?"] * (2 + len(columns)))
    col_names = ", ".join(columns)
    sql = (
        f"INSERT OR REPLACE INTO indicators (ticker, date, {col_names}) "
        f"VALUES ({placeholders})"
    )
    with get_connection() as conn:
        for date, row in df.iterrows():
            values = {db_col: row.get(src_col) for src_col, db_col in col_map.items()}
            values = {k: (None if pd.isna(v) else float(v)) for k, v in values.items()}
            conn.execute(sql, (ticker, date.strftime("%Y-%m-%d"),
                               *[values[c] for c in columns]))


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


def store_insider_trades(ticker: str, df: pd.DataFrame):
    """Store insider trade data. Upserts on (ticker, date, insider, transaction_type)."""
    if df is None or df.empty:
        return
    with get_connection() as conn:
        for _, row in df.iterrows():
            date_val = row.get("Start Date") or row.get("Date")
            if hasattr(date_val, "strftime"):
                date_str = date_val.strftime("%Y-%m-%d")
            else:
                date_str = str(date_val) if pd.notna(date_val) else ""
            shares = row.get("Shares")
            shares = int(shares) if pd.notna(shares) else None
            value = row.get("Value")
            value = float(value) if pd.notna(value) else None
            conn.execute(
                "INSERT OR REPLACE INTO insider_trades "
                "(ticker, date, insider, position, transaction_type, shares, value, ownership) "
                "VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                (ticker, date_str,
                 row.get("Insider") if pd.notna(row.get("Insider")) else None,
                 row.get("Position") if pd.notna(row.get("Position")) else None,
                 row.get("Text") or row.get("Transaction") if pd.notna(row.get("Text", row.get("Transaction"))) else None,
                 shares, value,
                 row.get("Ownership") if pd.notna(row.get("Ownership")) else None),
            )


def get_insider_trades(ticker: str = None) -> pd.DataFrame:
    """Get insider trades. If ticker is None, get all."""
    with get_connection() as conn:
        if ticker:
            df = pd.read_sql_query(
                "SELECT * FROM insider_trades WHERE ticker = ? ORDER BY date DESC",
                conn, params=(ticker,),
            )
        else:
            df = pd.read_sql_query(
                "SELECT * FROM insider_trades ORDER BY date DESC", conn,
            )
    if not df.empty:
        df["date"] = pd.to_datetime(df["date"], errors="coerce")
    return df


def get_last_fetch(ticker: str, data_type: str) -> str | None:
    """Return the last fetch date (ISO string) for a ticker/data_type, or None."""
    with get_connection() as conn:
        row = conn.execute(
            "SELECT last_fetch FROM fetch_log WHERE ticker = ? AND data_type = ?",
            (ticker, data_type),
        ).fetchone()
    return row[0] if row else None


def log_fetch(ticker: str, data_type: str):
    """Record today's date as the last fetch for ticker/data_type."""
    from datetime import date
    with get_connection() as conn:
        conn.execute(
            "INSERT OR REPLACE INTO fetch_log (ticker, data_type, last_fetch) "
            "VALUES (?, ?, ?)",
            (ticker, data_type, date.today().isoformat()),
        )


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


# --- News ---

def store_news(ticker: str, articles: list[dict]):
    """Store news articles. Each dict has: title, published, link, source."""
    with get_connection() as conn:
        for a in articles:
            conn.execute(
                "INSERT OR REPLACE INTO stock_news (ticker, published, title, link, source) "
                "VALUES (?, ?, ?, ?, ?)",
                (ticker, a.get("published", ""), a["title"],
                 a.get("link", ""), a.get("source", "")),
            )


def get_news(ticker: str = None) -> pd.DataFrame:
    """Get news articles. If ticker is None, get all."""
    with get_connection() as conn:
        if ticker:
            df = pd.read_sql_query(
                "SELECT * FROM stock_news WHERE ticker = ? ORDER BY published DESC",
                conn, params=(ticker,),
            )
        else:
            df = pd.read_sql_query(
                "SELECT * FROM stock_news ORDER BY published DESC", conn,
            )
    return df


# --- Earnings calendar ---

def store_earnings(ticker: str, earnings_date: str):
    """Store next earnings date for a ticker."""
    with get_connection() as conn:
        conn.execute(
            "INSERT OR REPLACE INTO earnings_calendar (ticker, earnings_date) "
            "VALUES (?, ?)",
            (ticker, earnings_date),
        )


def get_earnings() -> pd.DataFrame:
    with get_connection() as conn:
        df = pd.read_sql_query(
            "SELECT * FROM earnings_calendar ORDER BY earnings_date", conn,
        )
    return df


# --- Macro data ---

def store_macro(series_id: str, df: pd.DataFrame):
    """Store macro time-series data. df must have 'date' and 'value' columns or date index."""
    with get_connection() as conn:
        if "date" in df.columns:
            for _, row in df.iterrows():
                date_str = row["date"]
                if hasattr(date_str, "strftime"):
                    date_str = date_str.strftime("%Y-%m-%d")
                val = row["value"]
                if pd.notna(val):
                    conn.execute(
                        "INSERT OR REPLACE INTO macro_data (series_id, date, value) "
                        "VALUES (?, ?, ?)",
                        (series_id, date_str, float(val)),
                    )
        else:
            # date index
            for date_idx, row in df.iterrows():
                date_str = date_idx.strftime("%Y-%m-%d") if hasattr(date_idx, "strftime") else str(date_idx)
                val = row.iloc[0] if len(row) == 1 else row.get("value", row.iloc[0])
                if pd.notna(val):
                    conn.execute(
                        "INSERT OR REPLACE INTO macro_data (series_id, date, value) "
                        "VALUES (?, ?, ?)",
                        (series_id, date_str, float(val)),
                    )


def get_macro(series_id: str = None) -> pd.DataFrame:
    with get_connection() as conn:
        if series_id:
            df = pd.read_sql_query(
                "SELECT * FROM macro_data WHERE series_id = ? ORDER BY date",
                conn, params=(series_id,),
            )
        else:
            df = pd.read_sql_query(
                "SELECT * FROM macro_data ORDER BY series_id, date", conn,
            )
    if not df.empty:
        df["date"] = pd.to_datetime(df["date"])
    return df
