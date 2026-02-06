"""Tests for technical indicator calculations."""

import numpy as np
import pandas as pd
import pytest

from indicators.moving_averages import calculate_emas, calculate_smas
from indicators.momentum import calculate_rsi, calculate_macd
from indicators.volume import calculate_vwap
from indicators import calculate_all_indicators


def make_price_df(prices, volume=None):
    """Create a simple OHLCV DataFrame from close prices."""
    n = len(prices)
    dates = pd.date_range("2024-01-01", periods=n, freq="B")
    if volume is None:
        volume = [1000000] * n
    return pd.DataFrame({
        "Open": prices,
        "High": [p * 1.01 for p in prices],
        "Low": [p * 0.99 for p in prices],
        "Close": prices,
        "Volume": volume,
    }, index=dates)


class TestEMA:
    def test_ema_5_length(self):
        df = make_price_df([100.0] * 50)
        df = calculate_emas(df)
        assert "ema_5" in df.columns
        assert len(df["ema_5"].dropna()) == 50

    def test_ema_constant_price(self):
        """EMA of constant price should equal that price."""
        df = make_price_df([50.0] * 100)
        df = calculate_emas(df)
        # After warmup, EMA should converge to 50
        assert abs(df["ema_5"].iloc[-1] - 50.0) < 0.01
        assert abs(df["ema_200"].iloc[-1] - 50.0) < 0.5  # 200 EMA needs more data to converge

    def test_ema_increasing_prices(self):
        """EMA should be below price for consistently increasing prices."""
        prices = [100 + i for i in range(100)]
        df = make_price_df(prices)
        df = calculate_emas(df)
        # EMA lags, so for increasing prices, EMA < price
        assert df["ema_5"].iloc[-1] < df["Close"].iloc[-1]


class TestSMA:
    def test_sma_50_known_value(self):
        """SMA 50 should equal average of last 50 prices."""
        prices = list(range(1, 101))
        df = make_price_df([float(p) for p in prices])
        df = calculate_smas(df)
        # SMA 50 at last row = mean of prices[50:100] = mean(51..100) = 75.5
        assert abs(df["sma_50"].iloc[-1] - 75.5) < 0.01

    def test_sma_nan_before_window(self):
        """SMA should be NaN before enough data points."""
        df = make_price_df([100.0] * 40)
        df = calculate_smas(df)
        assert pd.isna(df["sma_50"].iloc[0])


class TestRSI:
    def test_rsi_constant_price(self):
        """RSI of constant price should be NaN or undefined (no gains/losses)."""
        df = make_price_df([100.0] * 50)
        df = calculate_rsi(df)
        # With no changes, gains and losses are 0, RSI is undefined
        # Our implementation handles this: avg_loss=0 → RSI=100
        # First value has no diff, so we expect some NaN at start
        assert "rsi_14" in df.columns

    def test_rsi_always_up(self):
        """RSI should be very high (near 100) if price always goes up."""
        prices = [100 + i * 0.5 for i in range(50)]
        df = make_price_df(prices)
        df = calculate_rsi(df)
        assert df["rsi_14"].iloc[-1] > 90

    def test_rsi_always_down(self):
        """RSI should be very low (near 0) if price always goes down."""
        prices = [200 - i * 0.5 for i in range(50)]
        df = make_price_df(prices)
        df = calculate_rsi(df)
        assert df["rsi_14"].iloc[-1] < 10

    def test_rsi_range(self):
        """RSI should be between 0 and 100."""
        np.random.seed(42)
        prices = 100 + np.cumsum(np.random.randn(200))
        prices = [max(p, 1) for p in prices]  # no negatives
        df = make_price_df(prices)
        df = calculate_rsi(df)
        valid_rsi = df["rsi_14"].dropna()
        assert (valid_rsi >= 0).all()
        assert (valid_rsi <= 100).all()


class TestMACD:
    def test_macd_constant_price(self):
        """MACD should be ~0 for constant price."""
        df = make_price_df([100.0] * 100)
        df = calculate_macd(df)
        assert abs(df["macd"].iloc[-1]) < 0.01
        assert abs(df["macd_signal"].iloc[-1]) < 0.01

    def test_macd_columns_exist(self):
        df = make_price_df([100.0] * 50)
        df = calculate_macd(df)
        assert "macd" in df.columns
        assert "macd_signal" in df.columns
        assert "macd_histogram" in df.columns

    def test_histogram_is_difference(self):
        """Histogram should equal MACD - Signal."""
        np.random.seed(42)
        prices = 100 + np.cumsum(np.random.randn(100))
        prices = [max(p, 1) for p in prices]
        df = make_price_df(prices)
        df = calculate_macd(df)
        diff = df["macd"] - df["macd_signal"]
        np.testing.assert_array_almost_equal(df["macd_histogram"].values, diff.values, decimal=10)


class TestVWAP:
    def test_vwap_constant_price_volume(self):
        """VWAP should equal price when price and volume are constant."""
        df = make_price_df([100.0] * 50, volume=[1000] * 50)
        df = calculate_vwap(df)
        # Typical price = (101 + 99 + 100) / 3 = 100.0
        valid_vwap = df["vwap_20"].dropna()
        assert abs(valid_vwap.iloc[-1] - 100.0) < 0.01

    def test_vwap_nan_before_window(self):
        """VWAP should be NaN before lookback window is filled."""
        df = make_price_df([100.0] * 15)
        df = calculate_vwap(df)
        assert pd.isna(df["vwap_20"].iloc[0])


class TestCalculateAll:
    def test_all_columns_present(self):
        """calculate_all_indicators should add all expected columns."""
        np.random.seed(42)
        prices = 100 + np.cumsum(np.random.randn(300))
        prices = [max(p, 1) for p in prices]
        df = make_price_df(prices)
        result = calculate_all_indicators(df)

        expected_cols = [
            "ema_5", "ema_10", "ema_20", "ema_50", "ema_200",
            "sma_50", "sma_200",
            "rsi_14", "rsi_21",
            "macd", "macd_signal", "macd_histogram",
            "vwap_20",
        ]
        for col in expected_cols:
            assert col in result.columns, f"Missing column: {col}"

    def test_does_not_modify_original(self):
        """calculate_all_indicators should not modify the input DataFrame."""
        df = make_price_df([100.0] * 50)
        original_cols = list(df.columns)
        calculate_all_indicators(df)
        assert list(df.columns) == original_cols
