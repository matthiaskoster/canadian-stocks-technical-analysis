"""Configuration for Canadian Large-Cap Stock Technical Analysis System."""

import os

# Database
DB_PATH = os.path.join(os.path.dirname(__file__), "data", "stocks.db")

# Data fetching
FETCH_DAYS = 450  # ~300 trading days

# Stock universe
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

OIL_GAS = {
    "CNQ.TO": "Canadian Natural Resources",
    "SU.TO": "Suncor Energy",
    "CVE.TO": "Cenovus Energy",
    "IMO.TO": "Imperial Oil",
    "WCP.TO": "Whitecap Resources",
    "TOU.TO": "Tourmaline Oil",
    "ARX.TO": "ARC Resources",
    "PEY.TO": "Peyto Exploration",
}

PIPELINES = {
    "ENB.TO": "Enbridge",
    "TRP.TO": "TC Energy",
    "PPL.TO": "Pembina Pipeline",
}

UTILITIES = {
    "EMA.TO": "Emera",
    "CPX.TO": "Capital Power",
}

TECH = {
    "SHOP.TO": "Shopify",
    "CSU.TO": "Constellation Software",
    "CLS.TO": "Celestica",
}

RAILS = {
    "CP.TO": "Canadian Pacific Kansas City",
    "CNR.TO": "Canadian National Railway",
}

TELECOM = {
    "BCE.TO": "BCE Inc",
    "T.TO": "Telus",
}

MINING = {
    "ABX.TO": "Barrick Gold",
    "FNV.TO": "Franco-Nevada",
    "CCO.TO": "Cameco",
    "DML.TO": "Denison Mines",
}

OTHER = {
    "BAM.TO": "Brookfield Asset Management",
    "BIP-UN.TO": "Brookfield Infrastructure",
}

# Legacy alias so existing imports of ENERGY still work
ENERGY = {**OIL_GAS, **PIPELINES}

ALL_STOCKS = {**BANKS, **OIL_GAS, **PIPELINES, **UTILITIES, **TECH, **RAILS, **TELECOM, **MINING, **OTHER}
TICKERS = list(ALL_STOCKS.keys())

SECTORS = {}
for t in BANKS:
    SECTORS[t] = "Banks"
for t in OIL_GAS:
    SECTORS[t] = "Oil & Gas"
for t in PIPELINES:
    SECTORS[t] = "Pipelines"
for t in UTILITIES:
    SECTORS[t] = "Utilities"
for t in TECH:
    SECTORS[t] = "Tech"
for t in RAILS:
    SECTORS[t] = "Rails"
for t in TELECOM:
    SECTORS[t] = "Telecom"
for t in MINING:
    SECTORS[t] = "Mining"
for t in OTHER:
    SECTORS[t] = "Other"

SECTOR_GROUPS = [
    ("Banks", BANKS),
    ("Oil & Gas", OIL_GAS),
    ("Pipelines", PIPELINES),
    ("Utilities", UTILITIES),
    ("Tech", TECH),
    ("Rails", RAILS),
    ("Telecom", TELECOM),
    ("Mining", MINING),
    ("Other", OTHER),
]
SECTOR_NAMES = [name for name, _ in SECTOR_GROUPS]

# ── US AI Stock Universe ──────────────────────────────────────────────────────
# Prices remain in USD — no currency conversion applied.

AI_SEMICONDUCTORS = {
    "NVDA": "NVIDIA",
    "AMD": "Advanced Micro Devices",
    "INTC": "Intel",
    "QCOM": "Qualcomm",
    "AVGO": "Broadcom",
    "ASML": "ASML Holding",
    "MRVL": "Marvell Technology",
    "TSM": "Taiwan Semiconductor (ADR)",
    "HYIX": "SK Hynix (ADR)",
    "MU": "Micron Technology",
}

AI_HYPERSCALERS = {
    "MSFT": "Microsoft",
    "GOOGL": "Alphabet",
    "AMZN": "Amazon",
    "META": "Meta",
    "AAPL": "Apple",
    "TSLA": "Tesla",
    "ORCL": "Oracle",
}

AI_ANALYTICS = {
    "PLTR": "Palantir Technologies",
    "CRWD": "CrowdStrike",
    "NET": "Cloudflare",
    "UPST": "Upstart Holdings",
    "SNOW": "Snowflake",
    "PANW": "Palo Alto Networks",
}

AI_SOFTWARE = {
    "CRM": "Salesforce",
    "ADBE": "Adobe",
    "APP": "AppLovin",
    "SMCI": "Super Micro Computer",
    "DELL": "Dell Technologies",
}

AI_EDA = {
    "SNPS": "Synopsys",
    "CDNS": "Cadence Design Systems",
}

AI_INFRASTRUCTURE = {
    "CRWV": "CoreWeave",
    "NBIS": "Nebius Group",
}

AI_MEMORY = {
    "SNDK": "SanDisk",
    "WDC": "Western Digital",
    "STX": "Seagate Technology",
    "CRSR": "Corsair",
}

AI_NETWORKING = {
    "ANET": "Arista Networks",
    "CSCO": "Cisco",
    "JNPR": "Juniper Networks",
}

AI_CHIPSET = {
    "RMBS": "Rambus",
    "SLAB": "Silicon Labs",
    "MTSI": "MACOM Technology",
    "PCTEL": "PC-Tel",
    "CRUS": "Cirrus Logic",
}

AI_MISC = {
    "IREN": "Iris Energy",
    "CLSK": "CleanSpark",
}

AI_ALL_STOCKS = {
    **AI_SEMICONDUCTORS,
    **AI_HYPERSCALERS,
    **AI_ANALYTICS,
    **AI_SOFTWARE,
    **AI_EDA,
    **AI_INFRASTRUCTURE,
    **AI_MEMORY,
    **AI_NETWORKING,
    **AI_CHIPSET,
    **AI_MISC,
}

AI_TICKERS = list(AI_ALL_STOCKS.keys())

AI_SECTORS = {}
for t in AI_SEMICONDUCTORS:
    AI_SECTORS[t] = "Semiconductors"
for t in AI_HYPERSCALERS:
    AI_SECTORS[t] = "Hyperscalers"
for t in AI_ANALYTICS:
    AI_SECTORS[t] = "Analytics"
for t in AI_SOFTWARE:
    AI_SECTORS[t] = "AI Software"
for t in AI_EDA:
    AI_SECTORS[t] = "EDA Tools"
for t in AI_INFRASTRUCTURE:
    AI_SECTORS[t] = "AI Infrastructure"
for t in AI_MEMORY:
    AI_SECTORS[t] = "Memory & Storage"
for t in AI_NETWORKING:
    AI_SECTORS[t] = "Networking"
for t in AI_CHIPSET:
    AI_SECTORS[t] = "Chipset Ecosystem"
for t in AI_MISC:
    AI_SECTORS[t] = "Misc AI"

AI_SECTOR_GROUPS = [
    ("Semiconductors", AI_SEMICONDUCTORS),
    ("Hyperscalers", AI_HYPERSCALERS),
    ("Analytics", AI_ANALYTICS),
    ("AI Software", AI_SOFTWARE),
    ("EDA Tools", AI_EDA),
    ("AI Infrastructure", AI_INFRASTRUCTURE),
    ("Memory & Storage", AI_MEMORY),
    ("Networking", AI_NETWORKING),
    ("Chipset Ecosystem", AI_CHIPSET),
    ("Misc AI", AI_MISC),
]

AI_SECTOR_NAMES = [name for name, _ in AI_SECTOR_GROUPS]

# Combined ticker list for the full pipeline (Canadian + US AI)
COMBINED_TICKERS = TICKERS + AI_TICKERS

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
    "GC=F": ["ABX.TO", "FNV.TO", "CCO.TO", "DML.TO"],
    "CL=F": ["CNQ.TO", "SU.TO", "CVE.TO", "IMO.TO", "WCP.TO"],
    "NG=F": ["ENB.TO", "TRP.TO", "PPL.TO", "TOU.TO", "ARX.TO", "PEY.TO"],
    "U-UN.TO": ["CCO.TO", "DML.TO"],
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

# Strategy thresholds
STOCH_OVERSOLD = 20
STOCH_OVERBOUGHT = 80
ATR_BREAKOUT_MULT = 1.5
ADX_TREND_THRESHOLD = 20
OBV_EMA_PERIOD = 20

# Backtesting
INITIAL_CAPITAL = 10000
