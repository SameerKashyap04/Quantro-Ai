"""
Quantro Personal AI — Shared Utilities
"""
from datetime import datetime, time
import pytz


def is_market_open(tz_name: str = "Asia/Kolkata") -> bool:
    """Check if the Indian stock market is currently open."""
    tz = pytz.timezone(tz_name)
    now = datetime.now(tz)
    
    # Weekend check
    if now.weekday() >= 5: # 5=Sat, 6=Sun
        return False
        
    market_open = time(9, 15)
    market_close = time(15, 30)
    current_time = now.time()
    
    return market_open <= current_time <= market_close


def get_market_date(tz_name: str = "Asia/Kolkata") -> str:
    """Get the current or last market date as a string (YYYY-MM-DD)."""
    tz = pytz.timezone(tz_name)
    now = datetime.now(tz)
    
    # If weekend, roll back to Friday
    if now.weekday() == 5: # Sat
        now = now.replace(day=now.day-1)
    elif now.weekday() == 6: # Sun
        now = now.replace(day=now.day-2)
        
    return now.strftime("%Y-%m-%d")


def round_to_tick(price: float, tick_size: float = 0.05) -> float:
    """Round a price to the nearest tick size (e.g., 0.05 for NSE)."""
    return round(round(price / tick_size) * tick_size, 2)


def calculate_position_size(
    account_value: float,
    risk_per_trade_pct: float,
    entry_price: float,
    stop_loss_price: float
) -> int:
    """Calculate the number of shares based on risk."""
    if entry_price <= stop_loss_price:
        return 0 # Invalid
        
    risk_amount = account_value * (risk_per_trade_pct / 100)
    risk_per_share = entry_price - stop_loss_price
    
    if risk_per_share <= 0:
        return 0
        
    return int(risk_amount / risk_per_share)
