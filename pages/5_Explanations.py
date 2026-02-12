"""Page 5: Explanations — Reference guide for all metrics and indicators."""

import streamlit as st

st.set_page_config(page_title="Explanations", page_icon="📖", layout="wide")
st.title("Metric & Indicator Explanations")
st.markdown("A reference guide for every metric, indicator, and signal used in this dashboard.")

# --- Moving Averages ---
with st.expander("Moving Averages (EMA & SMA)", expanded=False):
    st.markdown("""
**Exponential Moving Average (EMA)** gives more weight to recent prices, making it
more responsive to new information than a Simple Moving Average.

| Period | Use |
|--------|-----|
| EMA 5 | Ultra-short-term momentum |
| EMA 10 | Short-term trend |
| EMA 20 | Short-to-medium trend; common swing-trading reference |
| EMA 50 | Medium-term trend; institutional support/resistance level |
| EMA 200 | Long-term trend; widely watched by fund managers |

**Simple Moving Average (SMA)** weights all prices equally over the period.

| Period | Use |
|--------|-----|
| SMA 50 | Medium-term trend confirmation |
| SMA 200 | Long-term trend — the most-watched moving average on Wall Street |

**Distance from MA** — The percentage difference between the current price and a
moving average. A large positive distance means the stock is stretched above its
average (potentially overbought); a large negative distance means it may be oversold.

**Crossovers** — When a shorter MA crosses above a longer MA, it suggests upward
momentum (bullish). When it crosses below, it suggests downward momentum (bearish).
""")

# --- RSI ---
with st.expander("Relative Strength Index (RSI)", expanded=False):
    st.markdown("""
**RSI** measures the speed and magnitude of recent price changes on a 0-100 scale.

This dashboard uses **Wilder's smoothing** (exponential moving average with
`alpha = 1/period`), which is the original RSI method and gives a smoother,
less noisy reading than a standard EMA.

| Setting | Value |
|---------|-------|
| RSI(14) | Standard 14-period — most widely used |
| RSI(21) | Longer 21-period — smoother, fewer false signals |
| Overbought | RSI > 70 — price may be due for a pullback |
| Oversold | RSI < 30 — price may be due for a bounce |
| Midline | RSI = 50 — bullish when above, bearish when below |

**RSI Signals detected:**
- **RSI oversold bounce** — RSI crosses back above 30 after being below it (bullish)
- **RSI overbought reversal** — RSI crosses back below 70 after being above it (bearish)
- **RSI midline cross** — RSI crosses above or below 50 (trend confirmation)
""")

# --- MACD ---
with st.expander("MACD (Moving Average Convergence Divergence)", expanded=False):
    st.markdown("""
**MACD** tracks the relationship between two EMAs to identify trend changes.

| Component | Calculation |
|-----------|-------------|
| MACD Line | EMA(12) minus EMA(26) of closing price |
| Signal Line | EMA(9) of the MACD Line |
| Histogram | MACD Line minus Signal Line |

**Interpretation:**
- **MACD > Signal** (histogram positive) — Bullish momentum
- **MACD < Signal** (histogram negative) — Bearish momentum
- **MACD crosses above Signal** — Buy signal (bullish crossover)
- **MACD crosses below Signal** — Sell signal (bearish crossover)
- **MACD crosses zero** — Confirms trend direction change
- **Histogram shrinking** — Momentum fading, potential reversal ahead

The histogram visually shows the distance between MACD and its signal line.
Growing bars mean accelerating momentum; shrinking bars mean decelerating.
""")

# --- VWAP ---
with st.expander("VWAP (Volume-Weighted Average Price)", expanded=False):
    st.markdown("""
**VWAP** represents the average price a stock has traded at, weighted by volume.
Institutional traders use it as a benchmark for execution quality.

This dashboard uses a **rolling 20-day approximation**: the cumulative
(price x volume) divided by cumulative volume over the last 20 trading days.

**Interpretation:**
- **Price above VWAP** — Bullish; buyers are in control
- **Price below VWAP** — Bearish; sellers are in control
- **Price crossing VWAP** — Potential trend change
- **VWAP as support/resistance** — Price often bounces off VWAP during trends
""")

# --- Bollinger Bands ---
with st.expander("Bollinger Bands", expanded=False):
    st.markdown("""
**Bollinger Bands** place an upper and lower band around a moving average, based on
standard deviation. They expand during volatile periods and contract during calm ones.

| Component | Calculation |
|-----------|-------------|
| Middle Band | 20-period SMA |
| Upper Band | Middle + 2 standard deviations |
| Lower Band | Middle - 2 standard deviations |
| BB Width | (Upper - Lower) / Middle |

**Interpretation:**
- **Price touching upper band** — Stock may be overbought (especially if RSI > 70)
- **Price touching lower band** — Stock may be oversold (especially if RSI < 30)
- **Bollinger Squeeze** (BB Width contracting) — Low volatility, breakout imminent
- **Band expansion** — Trend is strengthening
- **Walking the band** — Strong trend; price repeatedly touching one band
""")

# --- ATR ---
with st.expander("ATR (Average True Range)", expanded=False):
    st.markdown("""
**ATR** measures market volatility by decomposing the entire range of a price
for a given period. Uses Wilder's smoothing (14-period).

**True Range** is the greatest of:
- Current High minus Current Low
- Abs(Current High minus Previous Close)
- Abs(Current Low minus Previous Close)

**Use cases:**
- **Dynamic stop-losses** — Set stops at 1.5x or 2x ATR below entry instead of fixed %
- **Position sizing** — Smaller positions when ATR is high (more volatile)
- **Volatility filter** — Avoid entering trades when ATR is unusually high
- **Breakout confirmation** — A breakout accompanied by rising ATR is more reliable
""")

# --- ADX ---
with st.expander("ADX (Average Directional Index)", expanded=False):
    st.markdown("""
**ADX** measures trend strength on a 0-100 scale, regardless of direction.
It uses +DI and -DI (directional indicators) to determine trend direction.

| ADX Value | Interpretation |
|-----------|---------------|
| < 20 | No trend / ranging market |
| 20-25 | Emerging trend |
| 25-50 | Strong trend |
| 50-75 | Very strong trend |
| > 75 | Extremely strong (rare) |

**+DI vs -DI:**
- **+DI > -DI** — Bullish trend (upward pressure dominates)
- **-DI > +DI** — Bearish trend (downward pressure dominates)
- **DI crossover** — Potential trend reversal

**Strategy filter:** Use ADX > 25 to confirm MA/EMA crossover signals. Use ADX < 20
to switch to mean-reversion strategies (RSI, Bollinger Bands).
""")

# --- OBV ---
with st.expander("OBV (On-Balance Volume)", expanded=False):
    st.markdown("""
**OBV** is a cumulative volume indicator that adds volume on up days and subtracts
it on down days. It reveals whether volume is flowing into or out of a stock.

**Interpretation:**
- **Rising OBV + Rising Price** — Uptrend confirmed by volume
- **Falling OBV + Falling Price** — Downtrend confirmed by volume
- **Rising OBV + Flat/Falling Price** — Accumulation; bullish divergence (smart money buying)
- **Falling OBV + Flat/Rising Price** — Distribution; bearish divergence (smart money selling)

OBV divergences are **leading indicators** — they often precede price moves by days
or weeks. Particularly useful for Canadian bank stocks where institutional flows dominate.
""")

# --- Stochastic ---
with st.expander("Stochastic Oscillator (%K / %D)", expanded=False):
    st.markdown("""
**Stochastic Oscillator** measures where the current close sits relative to the
high-low range over a lookback period (14 days). Scale: 0-100.

| Component | Calculation |
|-----------|-------------|
| %K | 100 x (Close - Lowest Low) / (Highest High - Lowest Low) over 14 periods |
| %D | 3-period SMA of %K (signal line) |

| Zone | Reading |
|------|---------|
| Overbought | > 80 |
| Oversold | < 20 |

**Stochastic vs RSI:**
- Stochastic works better in **sideways/ranging** markets
- RSI works better in **trending** markets
- Use ADX to decide: ADX < 20 → trust Stochastic; ADX > 25 → trust RSI
""")

# --- Signal Types ---
with st.expander("Signal Types", expanded=False):
    st.markdown("""
Signals are generated when specific technical conditions are met.

**Moving Average Crossover Signals:**
| Signal | Condition | Meaning |
|--------|-----------|---------|
| Golden Cross | SMA 50 crosses above SMA 200 | Major bullish trend reversal |
| Death Cross | SMA 50 crosses below SMA 200 | Major bearish trend reversal |
| EMA 5/20 Bullish | EMA 5 crosses above EMA 20 | Short-term uptrend starting |
| EMA 5/20 Bearish | EMA 5 crosses below EMA 20 | Short-term downtrend starting |
| EMA 10/50 Bullish | EMA 10 crosses above EMA 50 | Medium-term uptrend starting |
| EMA 10/50 Bearish | EMA 10 crosses below EMA 50 | Medium-term downtrend starting |

*Golden/Death Cross signals include a pullback filter to reduce false signals —
the cross is only confirmed after a small retracement.*

**RSI Signals:**
| Signal | Condition |
|--------|-----------|
| RSI Oversold Bounce | RSI(14) crosses above 30 |
| RSI Overbought Reversal | RSI(14) crosses below 70 |
| RSI Midline Bullish | RSI(14) crosses above 50 |
| RSI Midline Bearish | RSI(14) crosses below 50 |

**MACD Signals:**
| Signal | Condition |
|--------|-----------|
| MACD Bullish Crossover | MACD line crosses above signal line |
| MACD Bearish Crossover | MACD line crosses below signal line |

**Combined Momentum:**
When multiple indicators align (e.g., RSI bullish + MACD bullish + price above
VWAP), a combined momentum signal is generated for higher-confidence trades.
""")

# --- Backtest Metrics ---
with st.expander("Backtest Metrics", expanded=False):
    st.markdown("""
Backtesting applies a strategy to historical data to evaluate how it would
have performed. All backtests in this app use $10,000 starting capital.

| Metric | Definition |
|--------|-----------|
| **Total Trades** | Number of completed round-trip trades (entry + exit) |
| **Win Rate** | Percentage of trades that were profitable |
| **Avg Gain** | Average return on winning trades |
| **Avg Loss** | Average return on losing trades |
| **Risk/Reward Ratio** | Avg Gain divided by absolute Avg Loss — higher is better; >1.0 means winners are bigger than losers |
| **Max Drawdown** | Largest peak-to-trough decline during the backtest — measures worst-case risk |
| **Total Return** | Overall percentage return of the strategy |
| **Buy & Hold Return** | Return from simply buying and holding the stock over the same period |
| **Sharpe Ratio** | Risk-adjusted return (excess return / standard deviation). >1.0 is good, >2.0 is excellent |

**Strategy comparison:** A strategy is valuable when its Total Return exceeds
Buy & Hold Return with an acceptable Max Drawdown and a Sharpe Ratio > 1.0.
""")

# --- Insider Trading ---
with st.expander("Insider Trading", expanded=False):
    st.markdown("""
**Insider trading** (legal) refers to the buying and selling of a company's stock
by its officers, directors, and significant shareholders. These transactions must
be reported publicly.

**Why it matters:**
- **Insider buying** is generally seen as bullish — insiders are spending their own
  money because they believe the stock is undervalued
- **Insider selling** is less clear-cut — insiders may sell for personal reasons
  (diversification, taxes, expenses) rather than a negative outlook
- **Cluster buying** (multiple insiders buying around the same time) is a stronger
  bullish signal

**Ownership types:**
| Code | Meaning |
|------|---------|
| D | **Direct** — shares owned personally by the insider |
| I | **Indirect** — shares owned through a trust, family member, or entity |

**Transaction types:**
- **Purchase** / **Buy** — Insider bought shares on the open market
- **Sale** / **Sell** — Insider sold shares on the open market
- **Option Exercise** — Insider exercised stock options (less meaningful as a signal)
- **Automatic Sale/Purchase** — Pre-scheduled trades under a 10b5-1 plan (less meaningful)

**Best practice:** Focus on open-market purchases and sales rather than option
exercises or automatic transactions when evaluating insider sentiment.
""")

st.divider()
st.caption("All indicators and metrics are calculated from daily OHLCV data sourced from Yahoo Finance.")
