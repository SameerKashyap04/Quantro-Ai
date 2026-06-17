"""
Quantro Personal AI — Execution Executor
"""
import logging
from typing import Dict, Any

from services.execution_engine.modes import ExecutionModes
from services.risk_engine.validator import PreTradeValidator

logger = logging.getLogger(__name__)


class ExecutionEngine:
    """Main orchestrator for trade execution."""

    def __init__(
        self, 
        execution_modes: ExecutionModes, 
        validator: PreTradeValidator,
        current_mode: str = "paper"
    ):
        self.modes = execution_modes
        self.validator = validator
        self.current_mode = current_mode

    async def process_signal(self, signal: Dict[str, Any], account_state: Dict, holdings: list):
        """Convert a signal to an order and execute it according to the current mode."""
        
        # 1. Size the position
        # In a real flow, this calls RiskCalculator first
        quantity = 10  # Mock quantity for now
        price = 100.0  # Mock price
        
        order = {
            "id": f"ord_{signal.get('id', 'mock')}",
            "symbol": signal["symbol"],
            "order_type": signal["signal_type"],
            "quantity": quantity,
            "price": price,
            "stop_loss": signal.get("stop_loss_pct"), # Normally convert to absolute price
            "target": signal.get("target_pct"),
            "confidence": signal.get("confidence"),
            "strategy_name": signal.get("strategy_name")
        }
        
        # 2. Validate
        is_valid, reason = self.validator.validate_order(order, account_state.get("available_cash", 0), holdings)
        
        if not is_valid:
            logger.warning(f"Order validation failed: {reason}")
            return False
            
        # 3. Route to correct mode
        if self.current_mode == "paper":
            await self.modes.handle_paper_mode(order)
        elif self.current_mode == "approval":
            await self.modes.handle_approval_mode(order)
        elif self.current_mode == "auto":
            await self.modes.handle_auto_mode(order)
        else:
            logger.error(f"Unknown trading mode: {self.current_mode}")
            
        return True
