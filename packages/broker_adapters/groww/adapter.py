"""
Quantro Personal AI — Groww Adapter
"""
import logging
import asyncio
from typing import Dict, Any, List
from packages.broker_adapters.base import BaseBroker

try:
    from growwapi import GrowwAPI
except ImportError:
    GrowwAPI = None

logger = logging.getLogger(__name__)


class GrowwAdapter(BaseBroker):
    """
    Adapter for Groww Trading API using the official `growwapi` package.
    """

    def __init__(self, api_key: str, api_secret: str, access_token: str = None):
        self.api_key = api_key
        self.api_secret = api_secret
        self.access_token = access_token
        self.client = None
        
        if GrowwAPI is None:
            logger.error("growwapi package is not installed. Please run `pip install growwapi`")
            return
            
        if self.access_token:
            try:
                self.client = GrowwAPI(self.access_token)
                logger.info("Groww API initialized with access token.")
            except Exception as e:
                logger.error(f"Failed to initialize Groww API: {e}")

    async def authenticate(self) -> bool:
        logger.info("Groww API: Authenticating...")
        return self.client is not None

    async def get_profile(self) -> Dict[str, Any]:
        if not self.client:
            return {"broker": "groww", "status": "inactive", "error": "Client not initialized"}
            
        try:
            # We'll run this in a thread since growwapi is synchronous
            profile = await asyncio.to_thread(self.client.get_user_profile)
            return {"broker": "groww", "status": "active", "data": profile}
        except Exception as e:
            logger.error(f"Groww get_profile error: {e}")
            return {"broker": "groww", "status": "error"}

    async def get_funds(self) -> Dict[str, Any]:
        if not self.client:
            return {"available_cash": 0.0, "utilized_margin": 0.0}
        
        try:
            margin = await asyncio.to_thread(self.client.get_available_margin_details)
            # Adapt dict response as needed
            cash = margin.get('balance', 0.0) if isinstance(margin, dict) else 0.0
            return {"available_cash": float(cash), "utilized_margin": 0.0}
        except Exception as e:
            logger.error(f"Groww get_funds error: {e}")
            return {"available_cash": 0.0, "utilized_margin": 0.0}

    async def place_order(self, order_params: Dict[str, Any]) -> Dict[str, Any]:
        logger.warning(f"Groww API place_order not fully implemented. Params: {order_params}")
        return {"status": "REJECTED", "message": "API Not Implemented"}

    async def modify_order(self, order_id: str, new_params: Dict[str, Any]) -> Dict[str, Any]:
        return {}

    async def cancel_order(self, order_id: str) -> bool:
        return False

    async def get_order_history(self) -> list[Dict[str, Any]]:
        return []

    async def get_positions(self) -> list[Dict[str, Any]]:
        if not self.client:
            return []
            
        try:
            positions = await asyncio.to_thread(self.client.get_positions_for_user)
            return positions if isinstance(positions, list) else []
        except Exception as e:
            logger.error(f"Groww get_positions error: {e}")
            return []

    async def get_holdings(self) -> list[Dict[str, Any]]:
        """
        Fetches portfolio holdings using growwapi.
        Expected to return a list of dicts. We standardize them before returning.
        """
        if not self.client:
            logger.error("Groww client not initialized. Cannot fetch holdings.")
            return []
            
        try:
            raw_holdings = await asyncio.to_thread(self.client.get_holdings_for_user)
            logger.info(f"Groww API returned {len(raw_holdings) if isinstance(raw_holdings, list) else 0} holdings.")
            return raw_holdings if isinstance(raw_holdings, list) else [raw_holdings]
        except Exception as e:
            logger.error(f"Groww get_holdings error: {e}")
            return []
