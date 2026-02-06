# Canadian Large-Cap Stock Technical Analysis System

A Python-based technical analysis backtesting system for 25 Canadian large-cap stocks. Fetches historical data, calculates indicators, detects trading signals, backtests strategies, and displays results in an interactive Streamlit dashboard.

## Installation

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Usage

### Run the analysis pipeline

```bash
# All 25 stocks (fetches data + calculates everything)
python main.py

# Single stock
python main.py --ticker RY.TO

# Skip data fetching (use cached data)
python main.py --no-fetch

# Only fetch data, no analysis
python main.py --fetch-only
```

### Launch the dashboard

```bash
streamlit run streamlit_app.py
```

### Run tests

```bash
python -m pytest tests/ -v
```

## Stock Universe (25 stocks)

### Banks (8)
| Ticker | Name |
|--------|------|
| RY.TO | Royal Bank of Canada |
| TD.TO | Toronto-Dominion Bank |
| BNS.TO | Bank of Nova Scotia |
| BMO.TO | Bank of Montreal |
| CM.TO | CIBC |
| NA.TO | National Bank of Canada |
| MFC.TO | Manulife Financial |
| SLF.TO | Sun Life Financial |

### Energy (7)
| Ticker | Name |
|--------|------|
| CNQ.TO | Canadian Natural Resources |
| SU.TO | Suncor Energy |
| ENB.TO | Enbridge |
| TRP.TO | TC Energy |
| CVE.TO | Cenovus Energy |
| IMO.TO | Imperial Oil |
| PPL.TO | Pembina Pipeline |

### Other (10)
| Ticker | Name |
|--------|------|
| SHOP.TO | Shopify |
| CP.TO | Canadian Pacific Kansas City |
| CNR.TO | Canadian National Railway |
| BCE.TO | BCE Inc |
| T.TO | Telus |
| ABX.TO | Barrick Gold |
| FNV.TO | Franco-Nevada |
| CSU.TO | Constellation Software |
| ATD.TO | Alimentation Couche-Tard |
| WCN.TO | Waste Connections |

## Strategies

| Strategy | Entry | Exit |
|----------|-------|------|
| **EMA 10/50** | EMA 10 crosses above EMA 50 | EMA 10 crosses below EMA 50 |
| **EMA 5/20** | EMA 5 crosses above EMA 20 | EMA 5 crosses below EMA 20 |
| **RSI** | RSI(14) crosses above 30 (oversold recovery) | RSI(14) crosses below 70 (overbought reversal) |
| **MACD** | MACD line crosses above signal line | MACD line crosses below signal line |
| **VWAP** | Price crosses above 20-day VWAP | Price crosses below 20-day VWAP |
| **Combined** | EMA 10 > EMA 50, RSI > 50, MACD histogram > 0, price > VWAP | Opposite conditions align |

Additional signal types detected (not backtested as standalone):
- **Golden/Death Cross** — SMA 50/200 crossover with 3% pullback filter
- **RSI Midline Cross** — RSI(21) crossing the 50 level

## Dashboard Pages

1. **Live Signals** — Overview table of all 25 stocks with current price, MA distances, RSI, MACD status, VWAP position. Recent signals list.
2. **Stock Detail** — Individual stock deep dive with candlestick chart, indicator overlays, signal markers, RSI and MACD subplots.
3. **Backtest Results** — Strategy comparison tables, equity curves, win rate charts, rankings by Sharpe ratio.
4. **Sector Analysis** — Sector groupings (Banks/Energy/Other), comparative performance, return correlation heatmap.

## Technical Indicators

All indicators are calculated from scratch using pandas (no ta/pandas_ta dependency):

- **EMAs**: 5, 10, 20, 50, 200-day (`ewm(span=N)`)
- **SMAs**: 50, 200-day (`rolling(N).mean()`)
- **RSI**: 14 and 21-day using Wilder's smoothing (`ewm(alpha=1/period)`)
- **MACD**: 12/26/9 standard configuration
- **VWAP**: Rolling 20-day approximation using `sum(TP * Vol) / sum(Vol)`

## Project Structure

```
├── main.py                  # CLI orchestration script
├── streamlit_app.py         # Dashboard entry point
├── config.py                # Stock universe, parameters
├── requirements.txt
├── data/
│   ├── data_fetcher.py      # yfinance data fetching
│   └── database.py          # SQLite storage layer
├── indicators/
│   ├── moving_averages.py   # EMA, SMA
│   ├── momentum.py          # RSI, MACD
│   └── volume.py            # VWAP
├── strategies/
│   ├── ma_crossover.py      # MA crossover signals
│   ├── rsi_strategy.py      # RSI + MACD signals
│   └── combined_signals.py  # Multi-indicator signals
├── backtesting/
│   └── backtest_engine.py   # Trade simulation + metrics
├── dashboard/
│   └── components/
│       ├── charts.py        # Plotly chart factories
│       └── tables.py        # Table styling helpers
├── pages/
│   ├── 1_Live_Signals.py
│   ├── 2_Stock_Detail.py
│   ├── 3_Backtest_Results.py
│   └── 4_Sector_Analysis.py
└── tests/
    ├── test_indicators.py
    ├── test_signals.py
    └── test_backtest.py
```
