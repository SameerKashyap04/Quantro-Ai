"""
Quantro Personal AI — Risk Rules
"""
from typing import List, Dict, Any


class RiskRules:
    """Evaluates portfolio-level risk limits."""

    @staticmethod
    def check_max_positions(current_holdings: List[Dict], max_allowed: int) -> bool:
        """Check if adding a new position exceeds the limit."""
        return len(current_holdings) < max_allowed

    @staticmethod
    def check_sector_exposure(
        current_holdings: List[Dict], 
        new_sector: str, 
        new_value: float, 
        total_portfolio_value: float, 
        max_exposure_pct: float
    ) -> bool:
        """Check if adding the trade exceeds maximum allowed sector weight."""
        if total_portfolio_value <= 0:
            return True
            
        current_sector_value = sum(
            h.get("current_value", 0) for h in current_holdings 
            if h.get("sector") == new_sector
        )
        
        new_total = total_portfolio_value + new_value
        projected_sector_weight = ((current_sector_value + new_value) / new_total) * 100
        
        return projected_sector_weight <= max_exposure_pct
