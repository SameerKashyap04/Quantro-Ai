"""
Quantro Personal AI — Support/Resistance Indicator
"""
import pandas as pd
import numpy as np
from packages.indicators.base import BaseIndicator


class SupportResistance(BaseIndicator):
    """Basic Support and Resistance levels using local extrema."""

    def __init__(self, window: int = 10):
        self.window = window

    def calculate(self, df: pd.DataFrame) -> pd.DataFrame:
        self._validate_input(df, ["high", "low"])
        result = df.copy()
        
        # A simple method: rolling min/max
        result["resistance"] = df["high"].rolling(window=self.window, center=True).max()
        result["support"] = df["low"].rolling(window=self.window, center=True).min()
        
        # Forward fill to keep the last known level until a new one forms
        result["resistance"] = result["resistance"].ffill()
        result["support"] = result["support"].ffill()
        
        return result
