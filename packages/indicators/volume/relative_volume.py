"""
Quantro Personal AI — Relative Volume Indicator
"""
import pandas as pd
from packages.indicators.base import BaseIndicator


class RelativeVolume(BaseIndicator):
    """Relative Volume (RVOL)."""

    def __init__(self, period: int = 20):
        self.period = period

    def calculate(self, df: pd.DataFrame) -> pd.DataFrame:
        self._validate_input(df, ["volume"])
        result = df.copy()
        
        avg_volume = df["volume"].rolling(window=self.period).mean()
        result[f"rvol_{self.period}"] = df["volume"] / avg_volume
        
        return result
