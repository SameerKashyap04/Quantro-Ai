"""
Quantro Personal AI — Signal Filter
"""
from typing import Dict, Any


class SignalFilter:
    """Filters signals based on risk settings and quality thresholds."""

    def __init__(self, risk_settings: dict):
        self.risk_settings = risk_settings

    def passes_filter(self, signal: Dict[str, Any], market_regime: str) -> bool:
        """Check if a generated signal passes quality/risk filters."""
        
        # 1. Minimum Confidence
        if signal.get("confidence", 0) < 60:
            return False
            
        # 2. Stop Loss Sanity Check
        sl_pct = signal.get("stop_loss_pct", 100)
        max_sl = self.risk_settings.get("max_risk_per_trade_pct", 5.0)
        
        if sl_pct > (max_sl * 2): # Allow SL to be slightly wider than max risk if position size is reduced
            return False
            
        # 3. Regime Filter
        # Avoid taking LONGs in strong BEAR regimes unless confidence is extremely high
        if market_regime == "bear" and signal.get("signal_type") == "BUY":
            if signal.get("confidence", 0) < 85:
                return False
                
        if market_regime == "bull" and signal.get("signal_type") == "SELL":
            if signal.get("confidence", 0) < 85:
                return False
                
        return True
