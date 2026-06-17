"""
Quantro Personal AI — Portfolio Monitor
"""
import logging
from typing import List, Dict

logger = logging.getLogger(__name__)


class PortfolioMonitor:
    """Continuously monitors portfolio health and stop losses."""

    def __init__(self, alert_callback):
        self.alert_callback = alert_callback

    async def check_stop_losses(self, holdings: List[Dict], latest_prices: Dict[str, float]):
        """Check if any holdings have hit their stop loss levels."""
        triggered = []
        for holding in holdings:
            symbol = holding["symbol"]
            current_price = latest_prices.get(symbol)
            sl_price = holding.get("stop_loss_price")
            
            if current_price and sl_price:
                # Assuming long positions for now
                if current_price <= sl_price:
                    logger.warning(f"Stop loss triggered for {symbol} at {current_price} (SL: {sl_price})")
                    triggered.append(holding)
                    if self.alert_callback:
                        await self.alert_callback("STOP_LOSS", f"{symbol} hit SL at {current_price}")
                        
        return triggered
