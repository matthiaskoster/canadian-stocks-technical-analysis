# Technical Analysis Backtesting System for Canadian Large-Cap Stocks

## Project Overview
Build a Python-based technical analysis system that backtests multiple indicators on 25 Canadian large-cap stocks (primarily banks and oil & gas companies) over approximately 300 trading sessions. The system should identify profitable trading signals and create a dashboard to monitor when stocks hit key technical thresholds.

## Core Requirements

### 1. Data Collection (yfinance)
**Stock Universe (25 stocks):**

**Canadian Big 5 Banks:**
- RY.TO (Royal Bank of Canada)
- TD.TO (TD Bank)
- BNS.TO (Bank of Nova Scotia)
- BMO.TO (Bank of Montreal)
- CM.TO (CIBC)

**Additional Canadian Banks/Financials:**
- NA.TO (National Bank of Canada)
- MFC.TO (Manulife Financial)
- SLF.TO (Sun Life Financial)
- IFC.TO (Intact Financial)
- POW.TO (Power Corporation)

**Oil & Gas:**
- SU.TO (Suncor Energy)
- CNQ.TO (Canadian Natural Resources)
- IMO.TO (Imperial Oil)
- CVE.TO (Cenovus Energy)
- TOU.TO (Tourmaline Oil)
- ARX.TO (ARC Resources)
- WCP.TO (Whitecap Resources)

**Other Large Caps:**
- ENB.TO (Enbridge)
- CNR.TO (Canadian National Railway)
- CP.TO (Canadian Pacific Railway)
- SHOP.TO (Shopify)
- BCE.TO (BCE Inc)
- T.TO (Telus)
- NTR.TO (Nutrien)
- ABX.TO (Barrick Gold)

**Data Requirements:**
- Fetch ~300 trading sessions of historical data (approximately 1.5 years)
- Include: Open, High, Low, Close, Volume, Adjusted Close
- Handle missing data and stock splits appropriately

### 2. Technical Indicators to Calculate

**Moving Averages:**
- 5-day EMA
- 10-day EMA
- 20-day EMA
- 50-day SMA and EMA
- 200-day SMA and EMA

**VWAP:**
- Daily VWAP (reset each trading day)
- Note: VWAP requires intraday data for true accuracy, but approximate using daily OHLC

**RSI (Relative Strength Index):**
- RSI(14) - standard
- RSI(21) - specific to TSX backtesting

**MACD:**
- MACD(12,26,9) - standard settings
- MACD histogram

### 3. Signal Detection Rules

Implement the following proven strategies:

**A. Golden Cross / Death Cross (50/200 MA)**
- Golden Cross: 50-day MA crosses above 200-day MA → Bullish signal
- Death Cross: 50-day MA crosses below 200-day MA → Bearish signal
- Additional filter: Wait for pullback to 50-day MA before entry

**B. 10-day/50-day EMA Crossover**
- Buy: 10-day EMA crosses above 50-day EMA
- Sell: 10-day EMA crosses below 50-day EMA

**C. 5-day/20-day EMA Crossover**
- Buy: 5-day EMA crosses above 20-day EMA
- Sell: 5-day EMA crosses below 20-day EMA

**D. VWAP Signals**
- Price crosses above VWAP → Bullish
- Price crosses below VWAP → Bearish
- Track distance from VWAP (%)

**E. RSI Signals**
- RSI < 30 → Oversold (potential buy)
- RSI > 70 → Overbought (potential sell)
- RSI(21) crossing 50 level
- Track RSI divergences if possible

**F. MACD Signals**
- MACD line crosses above signal line → Bullish
- MACD line crosses below signal line → Bearish
- MACD histogram positive/negative

**G. Combined Signals (Higher Probability)**
- RSI oversold + MACD bullish cross + Price above 200-day MA
- RSI overbought + MACD bearish cross
- Price above all three key MAs (5, 50, 200) = strong uptrend

### 4. Backtesting Logic

For each stock and each strategy:
- Calculate entry/exit points based on signals
- Track hypothetical trades:
  - Entry date and price
  - Exit date and price
  - Hold period
  - Return (%)
  - Win/Loss
- Calculate performance metrics:
  - Win rate (%)
  - Average gain per trade
  - Average loss per trade
  - Risk/Reward ratio
  - Maximum drawdown
  - Total return vs buy-and-hold
  - Sharpe ratio (if feasible)

### 5. Data Storage

**Option A: CSV Files**
- `stock_data_raw.csv` - all raw price data
- `indicators_calculated.csv` - all calculated indicators
- `signals_detected.csv` - all buy/sell signals
- `backtest_results.csv` - performance summary by stock/strategy
- `current_positions.csv` - current technical status of each stock

**Option B: SQLite Database**
- Table: `stock_prices` (ticker, date, open, high, low, close, volume, adj_close)
- Table: `indicators` (ticker, date, ma_5, ma_10, ma_20, ma_50, ma_200, rsi_14, rsi_21, macd, macd_signal, macd_hist, vwap)
- Table: `signals` (ticker, date, signal_type, signal_name, direction, price)
- Table: `backtest_trades` (ticker, strategy, entry_date, entry_price, exit_date, exit_price, return_pct, hold_days)
- Table: `performance_summary` (ticker, strategy, win_rate, avg_gain, avg_loss, total_return, num_trades)

**Recommendation: Use SQLite for easier querying**

### 6. Dashboard Requirements

Create an interactive dashboard (recommend: Streamlit or Plotly Dash) with:

**Page 1: Live Signal Monitor**
- Table showing all 25 stocks with current status:
  - Current price
  - Distance from key MAs (50-day, 200-day)
  - RSI level with color coding (green <30, red >70)
  - MACD status (bullish/bearish)
  - Position relative to VWAP
  - Active signals (highlight stocks meeting combined criteria)
- Sortable and filterable
- Color-coded alerts for stocks hitting key thresholds

**Page 2: Stock Detail View**
- Dropdown to select individual stock
- Price chart with overlaid indicators:
  - Candlestick chart
  - 5, 50, 200-day MAs
  - VWAP
  - Buy/sell signals marked on chart
- Indicator panels:
  - RSI subplot
  - MACD subplot
- Recent signals table

**Page 3: Backtest Results**
- Strategy comparison table
- Performance by stock and strategy
- Equity curves
- Win rate visualizations
- Best performing strategies for banks vs energy stocks

**Page 4: Sector Analysis**
- Group by sector (Banks, Energy, Other)
- Comparative performance
- Correlation analysis

### 7. Technical Requirements

**Python Packages:**
```
yfinance
pandas
numpy
ta (Technical Analysis library) or pandas_ta
sqlite3 (built-in)
streamlit or plotly dash
plotly (for interactive charts)
matplotlib/seaborn (for static charts)
```

**Code Structure:**
```
project/
├── data/
│   ├── data_fetcher.py       # yfinance data collection
│   └── database.py            # SQLite operations
├── indicators/
│   ├── moving_averages.py
│   ├── momentum.py            # RSI, MACD
│   └── volume.py              # VWAP
├── strategies/
│   ├── ma_crossover.py
│   ├── rsi_strategy.py
│   └── combined_signals.py
├── backtesting/
│   └── backtest_engine.py
├── dashboard/
│   └── app.py                 # Streamlit/Dash app
├── main.py                    # Orchestration script
├── requirements.txt
└── README.md
```

### 8. Deliverables

1. **Fully functional Python codebase** with:
   - Data fetching and storage
   - Indicator calculations
   - Signal detection
   - Backtesting engine
   - Performance metrics

2. **Interactive dashboard** that:
   - Updates with latest data
   - Shows real-time signal status
   - Displays backtest results
   - Allows stock/strategy comparison

3. **Documentation** including:
   - Setup instructions
   - How to run backtests
   - How to interpret signals
   - Strategy performance summary

### 9. Special Considerations

**Canadian Market Specifics:**
- All tickers end in `.TO` for Toronto Stock Exchange
- Consider CAD/USD currency if needed
- Market hours: 9:30 AM - 4:00 PM EST
- Handle Canadian holidays

**Banks vs Energy:**
- Banks tend to be mean-reverting (RSI works well)
- Energy is more trend-following (MA crossovers work better)
- Consider separate strategy rankings by sector

**Data Quality:**
- Handle stock splits
- Manage missing data (holidays, halts)
- Validate unusual price movements

### 10. Optional Enhancements (if time permits)

- Email/SMS alerts when stocks hit key thresholds
- Automated daily updates
- Monte Carlo simulation for strategy robustness
- Walk-forward analysis
- Position sizing recommendations
- Portfolio-level backtesting (multiple stocks simultaneously)

## Success Criteria

The system should:
1. Successfully fetch and store data for all 25 stocks
2. Calculate all technical indicators accurately
3. Identify historical trading signals correctly
4. Generate meaningful backtest statistics
5. Display an intuitive dashboard showing current opportunities
6. Run efficiently (backtest should complete in < 5 minutes)
7. Be maintainable and extensible for future indicators

## Deployment Strategy

### Phase 1: Local Development + GitHub Backup (Start Here)

**Local Setup:**
- Develop and run everything on local machine
- SQLite database stored locally in `data/` directory
- Streamlit dashboard accessible at `http://localhost:8501`
- All code version-controlled with Git

**GitHub Repository Setup:**
Create a `.gitignore` file with:
```
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
venv/
env/
ENV/
.venv

# Data files (don't commit to GitHub)
*.db
*.sqlite
*.sqlite3
data/*.csv
data/*.json

# IDE
.vscode/
.idea/
*.swp
*.swo

# Environment variables
.env
.env.local

# OS
.DS_Store
Thumbs.db

# Jupyter Notebooks (optional)
.ipynb_checkpoints/
*.ipynb
```

**GitHub Workflow:**
```bash
# Initialize repo
git init
git add .
git commit -m "Initial commit: Canadian stock technical analysis system"

# Create GitHub repo (can be private initially)
# Then push:
git remote add origin https://github.com/YOUR_USERNAME/canadian-stocks-technical-analysis
git push -u origin main

# Regular updates:
git add .
git commit -m "Description of changes"
git push
```

**README.md Requirements:**
Include comprehensive documentation:
- Project description and features
- Installation instructions
- How to run locally
- How to run backtest
- How to launch dashboard
- Stock list and strategies explained
- Future: Streamlit Cloud deployment instructions

### Phase 2: Future Streamlit Community Cloud Deployment (Optional)

**When ready to deploy to Streamlit Cloud:**

**Code Requirements for Streamlit Cloud:**
1. Create `requirements.txt` in root:
```txt
yfinance
pandas
numpy
ta
streamlit
plotly
```

2. Create `streamlit_app.py` in root (entry point):
```python
# This file should import and run your dashboard
from dashboard.app import main
if __name__ == "__main__":
    main()
```

3. Ensure database path is configurable:
```python
# Use relative paths that work both locally and in cloud
import os
DB_PATH = os.path.join(os.path.dirname(__file__), 'data', 'stock_analysis.db')
```

**Deployment Steps (for future reference):**
1. Make GitHub repo public (required for free tier)
2. Go to https://share.streamlit.io
3. Sign in with GitHub
4. Click "New app"
5. Select your repo: `canadian-stocks-technical-analysis`
6. Set main file path: `streamlit_app.py` or `dashboard/app.py`
7. Click "Deploy"
8. App will be live at: `https://YOUR_USERNAME-canadian-stocks-technical-analysis.streamlit.app`

**Important Considerations for Cloud Deployment:**
- Free tier sleeps after inactivity (wakes in ~30 seconds when accessed)
- Limited to 1GB RAM on free tier (sufficient for 25 stocks)
- Database resets on each deploy unless you use Streamlit secrets or external DB
- Consider storing data in GitHub releases or cloud storage for persistence
- Set up caching with `@st.cache_data` to improve performance

**Data Persistence Options for Cloud:**
- **Option A:** Fetch fresh data each time app loads (slow but simple)
- **Option B:** Store pre-calculated data in GitHub repo (commit CSV files)
- **Option C:** Use external database (PostgreSQL on Supabase free tier)
- **Option D:** Use Streamlit secrets to store lightweight data

**Recommended Approach:**
- Start with local development (Phase 1)
- Keep GitHub repo private during development
- When satisfied with functionality, make repo public
- Deploy to Streamlit Cloud for remote access
- Keep local version as primary development environment

### Project File Structure for Both Local and Cloud

```
canadian-stocks-technical-analysis/
├── .gitignore                    # Exclude DB and data files
├── README.md                     # Comprehensive documentation
├── requirements.txt              # All dependencies
├── streamlit_app.py             # Entry point for Streamlit Cloud
├── config.py                     # Configuration (DB paths, stock list)
├── main.py                       # Local orchestration script
│
├── data/
│   ├── data_fetcher.py          # yfinance integration
│   ├── database.py              # SQLite operations
│   └── .gitkeep                 # Keep folder in Git (data files ignored)
│
├── indicators/
│   ├── __init__.py
│   ├── moving_averages.py
│   ├── momentum.py              # RSI, MACD
│   └── volume.py                # VWAP
│
├── strategies/
│   ├── __init__.py
│   ├── ma_crossover.py
│   ├── rsi_strategy.py
│   └── combined_signals.py
│
├── backtesting/
│   ├── __init__.py
│   └── backtest_engine.py
│
├── dashboard/
│   ├── __init__.py
│   ├── app.py                   # Main dashboard (can also be entry point)
│   ├── pages/
│   │   ├── 1_live_signals.py
│   │   ├── 2_stock_detail.py
│   │   ├── 3_backtest_results.py
│   │   └── 4_sector_analysis.py
│   └── components/
│       ├── charts.py
│       └── tables.py
│
└── tests/                       # Optional: unit tests
    └── __init__.py
```

## Getting Started

Please build this system step-by-step:

**Development Phase:**
1. Set up project structure and dependencies
2. Configure for local development with GitHub backup in mind
3. Implement data fetching with yfinance
4. Create database schema and storage (local SQLite)
5. Calculate technical indicators
6. Implement signal detection logic
7. Build backtesting engine
8. Create dashboard (Streamlit)
9. Test with actual data and validate results
10. Create comprehensive README with local setup instructions
11. Initialize Git repo and push to GitHub

**Future Deployment Phase (when ready):**
12. Prepare for Streamlit Cloud (ensure requirements.txt is complete)
13. Make repo public
14. Deploy to Streamlit Community Cloud
15. Test cloud deployment
16. Add cloud deployment instructions to README

Focus on code quality, proper error handling, and clear documentation. Make the system production-ready for local use, with easy path to cloud deployment later. 

**Key Priorities:**
- Works perfectly locally first
- Git-friendly structure (proper .gitignore)
- Configurable paths (works both locally and in cloud)
- Clear documentation for both local and cloud usage
- Professional code quality suitable for portfolio/client showcase
