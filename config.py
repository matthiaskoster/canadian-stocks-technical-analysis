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
    "WCN.TO": "Waste Connections",
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

# Indicator parameters
EMA_PERIODS = [5, 10, 20, 50, 200]
SMA_PERIODS = [50, 200]
RSI_PERIODS = [14, 21]
MACD_FAST = 12
MACD_SLOW = 26
MACD_SIGNAL = 9
VWAP_LOOKBACK = 20

# RSI thresholds
RSI_OVERSOLD = 30
RSI_OVERBOUGHT = 70
RSI_MIDLINE = 50

# Backtesting
INITIAL_CAPITAL = 10000
