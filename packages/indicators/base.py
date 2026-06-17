"""
Quantro Personal AI — Base Indicator
"""
from abc import ABC, abstractmethod
import pandas as pd


class BaseIndicator(ABC):
    """Abstract base class for all technical indicators."""

    @abstractmethod
    def calculate(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate the indicator values.
        
        Args:
            df: DataFrame containing at least 'close' column (and optionally open, high, low, volume)
            
        Returns:
            DataFrame with the new indicator columns added.
        """
        pass
        
    def _validate_input(self, df: pd.DataFrame, required_columns: list[str]) -> None:
        """Validate that the DataFrame has the required columns."""
        missing = [col for col in required_columns if col not in df.columns]
        if missing:
            raise ValueError(f"Missing required columns for indicator: {missing}")
