"""Configuration for Canadian Large-Cap Stock Technical Analysis System."""

import os

# Database
DB_PATH = os.path.join(os.path.dirname(__file__), "data", "stocks.db")

# Data fetching
FETCH_DAYS = 450  # ~300 trading days

# Stock universe — 25 Canadian large-cap stocks
BANKS = {
    "RY.TO": "Royal Bank of Canada",
    "TD.TO": "Toronto-Dominion Bank",
    "BNS.TO": "Bank of Nova Scotia",
    "BMO.TO": "Bank of Montreal",
    "CM.TO": "CIBC",
    "NA.TO": "National Bank of Canada",
    "MFC.TO": "Manulife Financial",
    "SLF.TO": "Sun Life Financial",
}

ENERGY = {
    "CNQ.TO": "Canadian Natural Resources",
    "SU.TO": "Suncor Energy",
    "ENB.TO": "Enbridge",
    "TRP.TO": "TC Energy",
    "CVE.TO": "Cenovus Energy",
    "IMO.TO": "Imperial Oil",
    "PPL.TO": "Pembina Pipeline",
}

OTHER = {
    "SHOP.TO": "Shopify",
    "CP.TO": "Canadian Pacific Kansas City",
    "CNR.TO": "Canadian National Railway",
    "BCE.TO": "BCE Inc",
    "T.TO": "Telus",
    "ABX.TO": "Barrick Gold",
    "FNV.TO": "Franco-Nevada",
    "CSU.TO": "Constellation Software",
    "ATD.TO": "Alimentation Couche-Tard",
    "WCP.TO": "Whitecap Resources",
}

ALL_STOCKS = {**BANKS, **ENERGY, **OTHER}
TICKERS = list(ALL_STOCKS.keys())

SECTORS = {}
for t in BANKS:
    SECTORS[t] = "Banks"
for t in ENERGY:
    SECTORS[t] = "Energy"
for t in OTHER:
    SECTORS[t] = "Other"

# Commodity tickers (fetched into stock_prices table alongside stocks)
COMMODITIES = {
    "GC=F": "Gold",
    "SI=F": "Silver",
    "HG=F": "Copper",
    "CL=F": "WTI Crude Oil",
    "NG=F": "Natural Gas",
    "BTC-USD": "Bitcoin",
    "U-UN.TO": "Uranium (Sprott Physical)",
}

COMMODITY_TICKERS = list(COMMODITIES.keys())

# Map commodities to related Canadian stocks for overlay charts
COMMODITY_STOCK_MAP = {
    "GC=F": ["ABX.TO", "FNV.TO"],
    "CL=F": ["CNQ.TO", "SU.TO", "CVE.TO", "IMO.TO"],
    "NG=F": ["ENB.TO", "TRP.TO", "PPL.TO"],
}

# Indicator parameters
EMA_PERIODS = [5, 10, 20, 50, 200]
SMA_PERIODS = [50, 200]
RSI_PERIODS = [14, 21]
MACD_FAST = 12
MACD_SLOW = 26
MACD_SIGNAL = 9
VWAP_LOOKBACK = 20
ATR_PERIOD = 14
BB_PERIOD = 20
BB_STD = 2
ADX_PERIOD = 14
STOCH_K_PERIOD = 14
STOCH_D_PERIOD = 3

# RSI thresholds
RSI_OVERSOLD = 30
RSI_OVERBOUGHT = 70
RSI_MIDLINE = 50

# FRED macro series
FRED_SERIES = {
    "DCOILWTICO": "WTI Crude Oil (USD/barrel)",
    "DEXCAUS": "USD/CAD Exchange Rate",
    "DGS10": "US 10-Year Treasury Yield",
}

# Backtesting
INITIAL_CAPITAL = 10000
