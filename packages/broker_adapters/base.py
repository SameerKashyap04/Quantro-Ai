"""
Quantro Personal AI — Base Broker Adapter
"""
from abc import ABC, abstractmethod
from typing import Optional, Dict, Any


class BaseBroker(ABC):
    """Abstract base class for all broker integrations."""

    @abstractmethod
    async def authenticate(self) -> bool:
        """Authenticate with the broker API."""
        pass

    @abstractmethod
    async def get_profile(self) -> Dict[str, Any]:
        """Get user profile and account details."""
        pass

    @abstractmethod
    async def get_funds(self) -> Dict[str, Any]:
        """Get available margins and funds."""
        pass

    @abstractmethod
    async def place_order(self, order_params: Dict[str, Any]) -> Dict[str, Any]:
        """Place a new order."""
        pass

    @abstractmethod
    async def modify_order(self, order_id: str, new_params: Dict[str, Any]) -> Dict[str, Any]:
        """Modify an existing pending order."""
        pass

    @abstractmethod
    async def cancel_order(self, order_id: str) -> bool:
        """Cancel an existing pending order."""
        pass

    @abstractmethod
    async def get_order_history(self) -> list[Dict[str, Any]]:
        """Get order history for the day."""
        pass

    @abstractmethod
    async def get_positions(self) -> list[Dict[str, Any]]:
        """Get current open positions."""
        pass

    @abstractmethod
    async def get_holdings(self) -> list[Dict[str, Any]]:
        """Get demat holdings (long term)."""
        pass
