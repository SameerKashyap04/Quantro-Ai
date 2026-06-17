"""
Quantro Personal AI — Portfolio Scorer
"""
import math
from typing import List, Dict


class PortfolioScorer:
    """Computes health and diversification scores for the portfolio."""

    @staticmethod
    def compute_diversification_score(holdings: List[Dict]) -> float:
        """
        Compute an entropy-based diversification score (0-100).
        100 = perfectly diversified across sectors.
        0 = 100% concentrated in a single sector.
        """
        if not holdings:
            return 0.0
            
        total_value = sum(h.get("current_value", 0) for h in holdings)
        if total_value <= 0:
            return 0.0
            
        # Aggregate by sector
        sector_weights = {}
        for h in holdings:
            sector = h.get("sector", "Unknown")
            val = h.get("current_value", 0)
            sector_weights[sector] = sector_weights.get(sector, 0) + val
            
        n_sectors = len(sector_weights)
        if n_sectors <= 1:
            return 0.0
            
        # Entropy Calculation
        entropy = 0
        for val in sector_weights.values():
            weight = val / total_value
            if weight > 0:
                entropy -= weight * math.log(weight)
                
        max_entropy = math.log(n_sectors)
        score = (entropy / max_entropy) * 100
        
        return round(score, 2)

    @staticmethod
    def compute_concentration_risk(holdings: List[Dict]) -> float:
        """
        Compute Herfindahl-Hirschman Index (HHI) for stock concentration.
        Scaled to 0-100 where higher is riskier.
        """
        if not holdings:
            return 0.0
            
        total_value = sum(h.get("current_value", 0) for h in holdings)
        if total_value <= 0:
            return 0.0
            
        hhi = 0
        for h in holdings:
            weight = h.get("current_value", 0) / total_value
            hhi += weight ** 2
            
        # HHI ranges from 1/N to 1.
        return round(hhi * 100, 2)
