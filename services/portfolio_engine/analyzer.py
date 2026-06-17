"""
Quantro Personal AI — Portfolio Analyzer
"""
import logging
from typing import List, Dict

logger = logging.getLogger(__name__)


class PortfolioAnalyzer:
    """Analyzes live portfolio holdings and generates performance reports."""

    @staticmethod
    def calculate_unrealized_pnl(holdings: List[Dict], latest_prices: Dict[str, float]) -> Dict[str, float]:
        """Calculate real-time unrealized PNL across all holdings."""
        total_invested = 0.0
        total_current = 0.0
        
        updated_holdings = []
        
        for holding in holdings:
            symbol = holding["symbol"]
            qty = holding["quantity"]
            avg_price = holding["avg_buy_price"]
            invested = qty * avg_price
            
            current_price = latest_prices.get(symbol, avg_price)
            current_val = qty * current_price
            pnl = current_val - invested
            pnl_pct = (pnl / invested * 100) if invested > 0 else 0
            
            total_invested += invested
            total_current += current_val
            
            h_copy = holding.copy()
            h_copy.update({
                "current_price": current_price,
                "current_value": current_val,
                "pnl": pnl,
                "pnl_pct": pnl_pct
            })
            updated_holdings.append(h_copy)
            
        total_pnl = total_current - total_invested
        total_pnl_pct = (total_pnl / total_invested * 100) if total_invested > 0 else 0
        
        return {
            "summary": {
                "total_invested": total_invested,
                "total_current": total_current,
                "total_pnl": total_pnl,
                "total_pnl_pct": total_pnl_pct
            },
            "holdings": updated_holdings
        }
