# Canadian Large-Cap Stock Technical Analysis System

A Python-based technical analysis backtesting system for 32 Canadian large-cap stocks and 7 commodities. Fetches historical data, calculates indicators, detects trading signals, backtests 11 strategies, and displays results in an interactive Streamlit dashboard.

## Installation

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Usage

### Run the analysis pipeline

```bash
# All 32 stocks + 7 commodities (fetches data + calculates everything)
python3 main.py

# Single stock
python3 main.py --ticker RY.TO

# Skip data fetching (use cached data)
python3 main.py --no-fetch

# Only fetch data, no analysis
python3 main.py --fetch-only

# Force full re-fetch
python3 main.py --force
```

### Launch the dashboard

```bash
streamlit run streamlit_app.py
```

### Run tests

```bash
python3 -m pytest tests/ -v
```

## Stock Universe (32 stocks across 8 sectors)

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

### Oil & Gas (8)
| Ticker | Name |
|--------|------|
| CNQ.TO | Canadian Natural Resources |
| SU.TO | Suncor Energy |
| CVE.TO | Cenovus Energy |
| IMO.TO | Imperial Oil |
| WCP.TO | Whitecap Resources |
| TOU.TO | Tourmaline Oil |
| ARX.TO | ARC Resources |
| PEY.TO | Peyto Exploration |

### Pipelines (3)
| Ticker | Name |
|--------|------|
| ENB.TO | Enbridge |
| TRP.TO | TC Energy |
| PPL.TO | Pembina Pipeline |

### Utilities (2)
| Ticker | Name |
|--------|------|
| EMA.TO | Emera |
| CPX.TO | Capital Power |

### Tech (3)
| Ticker | Name |
|--------|------|
| SHOP.TO | Shopify |
| CSU.TO | Constellation Software |
| CLS.TO | Celestica |

### Rails (2)
| Ticker | Name |
|--------|------|
| CP.TO | Canadian Pacific Kansas City |
| CNR.TO | Canadian National Railway |

### Telecom (2)
| Ticker | Name |
|--------|------|
| BCE.TO | BCE Inc |
| T.TO | Telus |

### Mining (4)
| Ticker | Name |
|--------|------|
| ABX.TO | Barrick Gold |
| FNV.TO | Franco-Nevada |
| CCO.TO | Cameco |
| DML.TO | Denison Mines |

## Commodities (7)
| Ticker | Name |
|--------|------|
| GC=F | Gold |
| SI=F | Silver |
| HG=F | Copper |
| CL=F | WTI Crude Oil |
| NG=F | Natural Gas |
| BTC-USD | Bitcoin |
| U-UN.TO | Uranium (Sprott Physical) |

## Strategies (11)

| Strategy | Entry | Exit |
|----------|-------|------|
| **EMA 10/50** | EMA 10 crosses above EMA 50 | EMA 10 crosses below EMA 50 |
| **EMA 5/20** | EMA 5 crosses above EMA 20 | EMA 5 crosses below EMA 20 |
| **RSI** | RSI(14) crosses above 30 (oversold recovery) | RSI(14) crosses below 70 (overbought reversal) |
| **MACD** | MACD line crosses above signal line | MACD line crosses below signal line |
| **VWAP** | Price crosses above 20-day VWAP | Price crosses below 20-day VWAP |
| **Combined** | EMA 10 > EMA 50, RSI > 50, MACD histogram > 0, price > VWAP | Opposite conditions align |
| **Bollinger Bands** | Price recovers above lower band | Price falls below upper band |
| **ATR Breakout** | Close > prev close + 1.5×ATR | Close < prev close - 1.5×ATR |
| **ADX DI Cross** | +DI crosses above -DI (ADX > 20) | -DI crosses above +DI (ADX > 20) |
| **OBV Trend** | OBV crosses above its 20-EMA | OBV crosses below its 20-EMA |
| **Stochastic** | %K crosses above %D below 20 | %K crosses below %D above 80 |

Additional signal types detected (not backtested as standalone):
- **Golden/Death Cross** — SMA 50/200 crossover with 3% pullback filter
- **RSI Midline Cross** — RSI(21) crossing the 50 level

## Dashboard Pages

1. **Live Signals** — Current indicator readings and recent signals for all 32 stocks
2. **Stock Detail** — Individual stock deep dive with candlestick chart, Bollinger Bands overlay, indicator subplots
3. **Backtest Results** — Strategy performance across 11 strategies with equity curves
4. **Sector Analysis** — Performance by sector with correlation heatmap
5. **Explanations** — Reference guide for all metrics, indicators, and signal types
6. **Insider Trading** — Insider buy/sell activity across all tracked stocks
7. **Commodities** — Gold, silver, copper, oil, natural gas, bitcoin, and uranium with related stock overlays
8. **News & Calendar** — Latest news and upcoming earnings dates
9. **Macro** — WTI crude, USD/CAD, US 10-year yield, and BoC overnight rate

## Technical Indicators

All indicators are calculated from scratch using pandas (no ta/pandas_ta dependency):

- **EMAs**: 5, 10, 20, 50, 200-day
- **SMAs**: 50, 200-day
- **RSI**: 14 and 21-day using Wilder's smoothing
- **MACD**: 12/26/9 standard configuration
- **VWAP**: Rolling 20-day approximation
- **Bollinger Bands**: 20-period, 2 std dev
- **ATR**: 14-period Average True Range
- **ADX**: 14-period with +DI/-DI
- **Stochastic**: %K(14)/%D(3)
- **OBV**: On-Balance Volume

## Project Structure

```
├── main.py                  # CLI orchestration script
├── streamlit_app.py         # Dashboard entry point
├── config.py                # Stock universe, parameters
├── requirements.txt
├── data/
│   ├── data_fetcher.py      # yfinance + FRED + BoC data fetching
│   └── database.py          # SQLite storage layer
├── indicators/
│   ├── moving_averages.py   # EMA, SMA
│   ├── momentum.py          # RSI, MACD, Stochastic
│   ├── volume.py            # VWAP, OBV
│   └── volatility.py        # ATR, Bollinger Bands, ADX
├── strategies/
│   ├── ma_crossover.py      # MA crossover signals
│   ├── rsi_strategy.py      # RSI + MACD signals
│   ├── combined_signals.py  # Multi-indicator signals
│   ├── bollinger_strategy.py
│   ├── atr_strategy.py
│   ├── adx_strategy.py
│   ├── obv_strategy.py
│   └── stochastic_strategy.py
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
│   ├── 4_Sector_Analysis.py
│   ├── 5_Explanations.py
│   ├── 6_Insider_Trading.py
│   ├── 7_Commodities.py
│   ├── 8_News_Calendar.py
│   └── 9_Macro.py
└── tests/
    ├── test_indicators.py
    ├── test_signals.py
    └── test_backtest.py
```
