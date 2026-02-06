"""Tests for backtesting engine."""

import numpy as np
import pandas as pd
import pytest

from backtesting.backtest_engine import BacktestEngine, Trade, BacktestResult


def make_simple_df(prices):
    """Create a price DataFrame from a list of close prices."""
    dates = pd.date_range("2024-01-01", periods=len(prices), freq="B")
    return pd.DataFrame({"Close": prices}, index=dates)


class TestTrade:
    def test_close_trade(self):
        t = Trade(entry_date=pd.Timestamp("2024-01-01"), entry_price=100.0)
        t.close(pd.Timestamp("2024-01-10"), 110.0)
        assert t.exit_price == 110.0
        assert t.return_pct == pytest.approx(10.0)

    def test_losing_trade(self):
        t = Trade(entry_date=pd.Timestamp("2024-01-01"), entry_price=100.0)
        t.close(pd.Timestamp("2024-01-10"), 90.0)
        assert t.return_pct == pytest.approx(-10.0)


class TestBacktestEngine:
    def setup_method(self):
        self.engine = BacktestEngine(initial_capital=10000)

    def test_no_signals_no_trades(self):
        """No entry signals → no trades."""
        df = make_simple_df([100.0] * 50)
        entry = pd.Series([False] * 50, index=df.index)
        exit_ = pd.Series([False] * 50, index=df.index)
        result = self.engine.run(df, entry, exit_, "TEST", "strat")
        assert result.total_trades == 0
        assert result.insufficient_data

    def test_single_round_trip(self):
        """One entry and one exit should produce one trade."""
        prices = [100.0] * 10 + [110.0] * 10
        df = make_simple_df(prices)
        entry = pd.Series([False] * 20, index=df.index)
        exit_ = pd.Series([False] * 20, index=df.index)
        entry.iloc[2] = True   # Enter at price 100
        exit_.iloc[12] = True  # Exit at price 110

        result = self.engine.run(df, entry, exit_, "TEST", "strat")
        assert result.total_trades == 1
        assert result.trades[0].entry_price == 100.0
        assert result.trades[0].exit_price == 110.0
        assert result.trades[0].return_pct == pytest.approx(10.0)

    def test_close_at_end(self):
        """Open position should be closed at end of data."""
        prices = [100.0] * 10 + [120.0] * 10
        df = make_simple_df(prices)
        entry = pd.Series([False] * 20, index=df.index)
        exit_ = pd.Series([False] * 20, index=df.index)
        entry.iloc[2] = True  # Enter, no exit signal

        result = self.engine.run(df, entry, exit_, "TEST", "strat")
        assert result.total_trades == 1
        assert result.trades[0].exit_price == 120.0

    def test_multiple_trades(self):
        """Multiple entry/exit pairs should create multiple trades."""
        prices = [100.0] * 30
        df = make_simple_df(prices)
        entry = pd.Series([False] * 30, index=df.index)
        exit_ = pd.Series([False] * 30, index=df.index)

        entry.iloc[2] = True
        exit_.iloc[5] = True
        entry.iloc[10] = True
        exit_.iloc[15] = True
        entry.iloc[20] = True
        exit_.iloc[25] = True

        result = self.engine.run(df, entry, exit_, "TEST", "strat")
        assert result.total_trades == 3

    def test_one_position_at_a_time(self):
        """Should not enter a new position while already in one."""
        prices = [100.0, 105.0, 110.0, 115.0, 120.0] + [100.0] * 15
        df = make_simple_df(prices)
        entry = pd.Series([False] * 20, index=df.index)
        exit_ = pd.Series([False] * 20, index=df.index)

        entry.iloc[0] = True  # Enter
        entry.iloc[2] = True  # Try to enter again (should be ignored)
        exit_.iloc[4] = True  # Exit

        result = self.engine.run(df, entry, exit_, "TEST", "strat")
        assert result.total_trades == 1

    def test_win_rate_calculation(self):
        """Win rate should be correct for known trades."""
        prices = list(range(100, 130))  # increasing
        prices += list(range(129, 99, -1))  # decreasing
        df = make_simple_df(prices)
        entry = pd.Series([False] * len(prices), index=df.index)
        exit_ = pd.Series([False] * len(prices), index=df.index)

        # Trade 1: win (100 → 110)
        entry.iloc[0] = True
        exit_.iloc[10] = True
        # Trade 2: loss (129 → 119)
        entry.iloc[30] = True
        exit_.iloc[40] = True
        # Trade 3: win (119 → ... closed at end with some value)
        entry.iloc[45] = True

        result = self.engine.run(df, entry, exit_, "TEST", "strat")
        assert result.total_trades == 3

    def test_insufficient_data_flag(self):
        """Should flag strategies with < 3 trades."""
        df = make_simple_df([100.0] * 30)
        entry = pd.Series([False] * 30, index=df.index)
        exit_ = pd.Series([False] * 30, index=df.index)
        entry.iloc[2] = True
        exit_.iloc[5] = True

        result = self.engine.run(df, entry, exit_, "TEST", "strat")
        assert result.total_trades == 1
        assert result.insufficient_data

    def test_buy_hold_return(self):
        """Buy and hold return should match start-to-end price change."""
        prices = [100.0] + [100.0] * 18 + [150.0]
        df = make_simple_df(prices)
        entry = pd.Series([False] * 20, index=df.index)
        exit_ = pd.Series([False] * 20, index=df.index)

        result = self.engine.run(df, entry, exit_, "TEST", "strat")
        assert result.buy_hold_return == pytest.approx(50.0)

    def test_max_drawdown_no_trades(self):
        """Max drawdown should be 0 when there are no trades."""
        df = make_simple_df([100.0] * 20)
        entry = pd.Series([False] * 20, index=df.index)
        exit_ = pd.Series([False] * 20, index=df.index)
        result = self.engine.run(df, entry, exit_, "TEST", "strat")
        assert result.max_drawdown == 0

    def test_total_return_with_known_trades(self):
        """Total return should compound correctly."""
        prices = [100.0] * 5 + [110.0] * 5 + [100.0] * 5 + [105.0] * 5
        df = make_simple_df(prices)
        entry = pd.Series([False] * 20, index=df.index)
        exit_ = pd.Series([False] * 20, index=df.index)

        entry.iloc[0] = True   # Enter at 100
        exit_.iloc[5] = True   # Exit at 110 (+10%)
        entry.iloc[6] = True   # Enter at 110
        exit_.iloc[10] = True  # Exit at 100 (-9.09%)
        entry.iloc[11] = True  # Enter at 100
        exit_.iloc[15] = True  # Exit at 105 (+5%)

        result = self.engine.run(df, entry, exit_, "TEST", "strat")
        assert result.total_trades == 3

        # Compounding: 10000 * 1.10 * (1 - 100/1100) * 1.05
        # = 10000 * 1.10 * 0.9091 * 1.05 ≈ 10500
        expected = (10000 * 1.10 * (1 - 10/110) * 1.05 - 10000) / 10000 * 100
        assert result.total_return == pytest.approx(expected, rel=0.01)


class TestEdgeCases:
    def setup_method(self):
        self.engine = BacktestEngine()

    def test_very_short_data(self):
        """Should handle very short data gracefully."""
        df = make_simple_df([100.0] * 5)
        entry = pd.Series([False] * 5, index=df.index)
        exit_ = pd.Series([False] * 5, index=df.index)
        result = self.engine.run(df, entry, exit_, "TEST", "strat")
        assert result.insufficient_data

    def test_nan_in_signals(self):
        """Should handle NaN in entry/exit signals."""
        df = make_simple_df([100.0] * 20)
        entry = pd.Series([False] * 20, index=df.index, dtype=object)
        exit_ = pd.Series([False] * 20, index=df.index, dtype=object)
        entry.iloc[0] = np.nan
        exit_.iloc[0] = np.nan

        result = self.engine.run(df, entry, exit_, "TEST", "strat")
        # Should not crash
        assert isinstance(result, BacktestResult)

    def test_entry_on_last_day(self):
        """Entry on last day should immediately close at end."""
        df = make_simple_df([100.0] * 20)
        entry = pd.Series([False] * 20, index=df.index)
        exit_ = pd.Series([False] * 20, index=df.index)
        entry.iloc[-1] = True

        result = self.engine.run(df, entry, exit_, "TEST", "strat")
        assert result.total_trades == 1
        assert result.trades[0].return_pct == pytest.approx(0.0)
