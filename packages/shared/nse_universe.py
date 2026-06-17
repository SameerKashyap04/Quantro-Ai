"""
Quantro Personal AI — NSE Universe Definition
Contains hardcoded lists of major Indian stock symbols for fallback/bootstrapping.
"""

NIFTY_50 = [
    "ADANIENT", "ADANIPORTS", "APOLLOHOSP", "ASIANPAINT", "AXISBANK",
    "BAJAJ-AUTO", "BAJFINANCE", "BAJAJFINSV", "BPCL", "BHARTIARTL",
    "BRITANNIA", "CIPLA", "COALINDIA", "DIVISLAB", "DRREDDY",
    "EICHERMOT", "GRASIM", "HCLTECH", "HDFCBANK", "HDFCLIFE",
    "HEROMOTOCO", "HINDALCO", "HINDUNILVR", "ICICIBANK", "ITC",
    "INDUSINDBK", "INFY", "JSWSTEEL", "KOTAKBANK", "LTIM",
    "LT", "M&M", "MARUTI", "NTPC", "NESTLEIND",
    "ONGC", "POWERGRID", "RELIANCE", "SBILIFE", "SBIN",
    "SUNPHARMA", "TCS", "TATACONSUM", "TATAMOTORS", "TATASTEEL",
    "TECHM", "TITAN", "ULTRACEMCO", "WIPRO", "SHRIRAMFIN"
]

NIFTY_NEXT_50 = [
    "ABB", "AMBUJACEM", "AUROPHARMA", "DMART", "BAJAJHLDNG",
    "BANKBARODA", "BERGEPAINT", "BEL", "BOSCHLTD", "CANBK",
    "CHOLAFIN", "COLPAL", "DLF", "DABUR", "GAIL",
    "GODREJCP", "HAVELLS", "HAL", "ICICIGI", "ICICIPRULI",
    "IOC", "IRCTC", "IRFC", "JINDALSTEL", "JIOFIN",
    "KALYANKJIL", "LICI", "MARICO", "MUTHOOTFIN", "NAUKRI",
    "PIIND", "PIDILITIND", "PFC", "PNB", "RECLTD",
    "SRF", "MOTHERSON", "SHREECEM", "SIEMENS", "TVSMOTOR",
    "TORNTPHARM", "TRENT", "UBL", "UNITDSPR", "VBL",
    "VEDL", "ZOMATO", "ZYDUSLIFE"
]

KEY_INDICES = {
    "NIFTY": "^NSEI",
    "BANKNIFTY": "^NSEBANK",
    "FINNIFTY": "NIFTY_FIN_SERVICE.NS",
    "MIDCAP": "^NSEMDCP50"
}

KEY_ETFS = [
    "NIFTYBEES", "BANKBEES", "GOLDBEES", "JUNIORBEES", 
    "LIQUIDBEES", "SILVERBEES", "ITBEES", "PHARMABEES"
]

def get_yfinance_symbol(symbol: str, is_index: bool = False) -> str:
    """Format an NSE symbol for yfinance."""
    if is_index:
        return KEY_INDICES.get(symbol, f"^{symbol}")
    if not symbol.endswith(".NS") and not symbol.endswith(".BO"):
        return f"{symbol}.NS"
    return symbol
