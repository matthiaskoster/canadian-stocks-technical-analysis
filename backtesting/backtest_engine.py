"""Backtesting engine for evaluating trading strategies."""

from dataclasses import dataclass, field

import numpy as np
import pandas as pd

from config import INITIAL_CAPITAL


@dataclass
class Trade:
    entry_date: pd.Timestamp
    entry_price: float
    exit_date: pd.Timestamp | None = None
    exit_price: float | None = None
    return_pct: float | None = None
    direction: str = "long"

    def close(self, exit_date: pd.Timestamp, exit_price: float):
        self.exit_date = exit_date
        self.exit_price = exit_price
        self.return_pct = (exit_price - self.entry_price) / self.entry_price * 100


@dataclass
class BacktestResult:
    strategy: str
    ticker: str
    trades: list[Trade] = field(default_factory=list)
    total_trades: int = 0
    win_rate: float = 0.0
    avg_gain: float = 0.0
    avg_loss: float = 0.0
    risk_reward: float = 0.0
    max_drawdown: float = 0.0
    total_return: float = 0.0
    buy_hold_return: float = 0.0
    sharpe_ratio: float = 0.0
    insufficient_data: bool = False


class BacktestEngine:
    """Simple day-by-day backtester. One position at a time, entry/exit on close."""

    def __init__(self, initial_capital: float = INITIAL_CAPITAL):
        self.initial_capital = initial_capital

    def run(
        self,
        df: pd.DataFrame,
        entry_signals: pd.Series,
        exit_signals: pd.Series,
        ticker: str,
        strategy_name: str,
    ) -> BacktestResult:
        """Run backtest on a single stock/strategy combination.

        Args:
            df: Price DataFrame with DatetimeIndex and 'Close' column.
            entry_signals: Boolean Series aligned with df index (True = enter long).
            exit_signals: Boolean Series aligned with df index (True = exit long).
            ticker: Stock ticker symbol.
            strategy_name: Name of the strategy.
        """
        result = BacktestResult(strategy=strategy_name, ticker=ticker)

        # Drop NaN rows from signals
        valid = entry_signals.notna() & exit_signals.notna()
        df = df[valid].copy()
        entry_signals = entry_signals[valid]
        exit_signals = exit_signals[valid]

        if len(df) < 10:
            result.insufficient_data = True
            return result

        trades = []
        in_position = False
        current_trade = None

        for i in range(len(df)):
            date = df.index[i]
            close = df["Close"].iloc[i]

            if not in_position and entry_signals.iloc[i]:
                current_trade = Trade(entry_date=date, entry_price=close)
                in_position = True
            elif in_position and exit_signals.iloc[i]:
                current_trade.close(date, close)
                trades.append(current_trade)
                current_trade = None
                in_position = False

        # Close open position at end of data
        if in_position and current_trade is not None:
            last_date = df.index[-1]
            last_close = df["Close"].iloc[-1]
            current_trade.close(last_date, last_close)
            trades.append(current_trade)

        result.trades = trades
        result.total_trades = len(trades)

        if result.total_trades < 3:
            result.insufficient_data = True

        # Calculate metrics
        if trades:
            returns = [t.return_pct for t in trades if t.return_pct is not None]
            wins = [r for r in returns if r > 0]
            losses = [r for r in returns if r <= 0]

            result.win_rate = len(wins) / len(returns) * 100 if returns else 0
            result.avg_gain = np.mean(wins) if wins else 0
            result.avg_loss = np.mean(losses) if losses else 0
            result.risk_reward = (
                abs(result.avg_gain / result.avg_loss) if result.avg_loss != 0 else float("inf")
            )

            # Total return (compounding)
            capital = self.initial_capital
            for r in returns:
                capital *= (1 + r / 100)
            result.total_return = (capital - self.initial_capital) / self.initial_capital * 100

            # Max drawdown from equity curve
            equity = [self.initial_capital]
            for r in returns:
                equity.append(equity[-1] * (1 + r / 100))
            equity = np.array(equity)
            peak = np.maximum.accumulate(equity)
            drawdown = (equity - peak) / peak * 100
            result.max_drawdown = drawdown.min()

            # Sharpe ratio (annualized, assuming ~252 trading days)
            if len(returns) > 1:
                returns_arr = np.array(returns) / 100
                avg_return = np.mean(returns_arr)
                std_return = np.std(returns_arr, ddof=1)
                if std_return > 0:
                    # Approximate annualization: scale by sqrt of trades per year
                    trades_per_year = 252 / max(len(df) / len(returns), 1)
                    result.sharpe_ratio = (avg_return / std_return) * np.sqrt(trades_per_year)
                else:
                    result.sharpe_ratio = 0.0
            else:
                result.sharpe_ratio = 0.0

        # Buy and hold return
        if len(df) >= 2:
            result.buy_hold_return = (
                (df["Close"].iloc[-1] - df["Close"].iloc[0]) / df["Close"].iloc[0] * 100
            )

        return result
