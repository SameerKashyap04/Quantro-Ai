"""
Quantro Personal AI — Emergency Halt System
"""
import logging
from services.risk_engine.calculator import RiskCalculator

logger = logging.getLogger(__name__)


class EmergencySystem:
    """Manages the killswitch to halt trading during extreme drawdowns."""

    def __init__(self, halt_callback):
        self.halt_callback = halt_callback

    async def check_daily_drawdown(
        self, 
        start_of_day_equity: float, 
        current_equity: float, 
        max_dd_limit_pct: float
    ):
        """Check if daily drawdown limit is breached."""
        dd = RiskCalculator.calculate_drawdown(start_of_day_equity, current_equity)
        
        if dd >= max_dd_limit_pct:
            logger.critical(f"EMERGENCY: Daily drawdown {dd:.2f}% breached limit {max_dd_limit_pct}%!")
            if self.halt_callback:
                await self.halt_callback("DRAWDOWN_LIMIT", f"Drawdown {dd:.2f}% breached limit.")
            return True
        return False
