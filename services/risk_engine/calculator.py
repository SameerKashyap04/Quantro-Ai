"""
Quantro Personal AI — Risk Calculator
"""
import math
from typing import Dict, Any


class RiskCalculator:
    """Calculates position sizing and risk metrics."""

    @staticmethod
    def calculate_position_size(
        capital: float, 
        risk_per_trade_pct: float, 
        entry_price: float, 
        stop_loss_price: float
    ) -> int:
        """
        Calculate the number of shares based on account risk percentage.
        E.g., $100k account, 1% risk = $1000 at risk.
        If entry is 100, SL is 90, risk per share is $10.
        Shares = 1000 / 10 = 100 shares.
        """
        if entry_price <= 0 or stop_loss_price <= 0:
            return 0
            
        risk_per_share = abs(entry_price - stop_loss_price)
        if risk_per_share == 0:
            return 0
            
        capital_at_risk = capital * (risk_per_trade_pct / 100)
        
        shares = math.floor(capital_at_risk / risk_per_share)
        
        # Additional constraint: don't exceed available capital (no leverage)
        max_shares = math.floor(capital / entry_price)
        
        return min(shares, max_shares)

    @staticmethod
    def calculate_drawdown(peak_value: float, current_value: float) -> float:
        """Calculate percentage drawdown from peak."""
        if peak_value <= 0:
            return 0.0
        dd = (peak_value - current_value) / peak_value * 100
        return max(0.0, dd)
