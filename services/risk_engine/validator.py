"""
Quantro Personal AI — Pre-Trade Validator
"""
import logging
from typing import Dict, Any, Tuple, List

from services.risk_engine.calculator import RiskCalculator
from services.risk_engine.rules import RiskRules
from packages.shared.models import RiskConfig

logger = logging.getLogger(__name__)


class PreTradeValidator:
    """Validates an order before it is sent to the broker."""

    def __init__(self, risk_config: RiskConfig):
        self.config = risk_config

    def validate_order(
        self, 
        order: Dict[str, Any], 
        account_funds: float, 
        current_holdings: List[Dict]
    ) -> Tuple[bool, str]:
        """
        Run all pre-trade checks.
        Returns (is_valid, reason_if_invalid)
        """
        # 1. Capital Check
        required_capital = order.get("quantity", 0) * order.get("price", 0)
        if required_capital > account_funds:
            return False, f"Insufficient funds. Requires {required_capital}, available {account_funds}"
            
        # 2. Max Positions Check
        if order.get("order_type") == "BUY":
            symbol = order.get("symbol")
            already_holding = any(h.get("symbol") == symbol for h in current_holdings)
            
            if not already_holding and not RiskRules.check_max_positions(current_holdings, self.config.max_open_positions):
                return False, f"Max open positions limit ({self.config.max_open_positions}) reached."

        # 3. Sector Exposure (if sector info is provided)
        if order.get("order_type") == "BUY" and order.get("sector"):
            total_value = sum(h.get("current_value", 0) for h in current_holdings) + account_funds
            if not RiskRules.check_sector_exposure(
                current_holdings, 
                order["sector"], 
                required_capital, 
                total_value, 
                self.config.max_sector_exposure_pct
            ):
                return False, f"Adding trade exceeds max sector exposure ({self.config.max_sector_exposure_pct}%)."
                
        return True, "Valid"
