"""
Quantro Personal AI — SMA Indicator
"""
import pandas as pd
from packages.indicators.base import BaseIndicator


class SMA(BaseIndicator):
    """Simple Moving Average."""

    def __init__(self, periods: list[int] = [20, 50, 200]):
        self.periods = periods

    def calculate(self, df: pd.DataFrame) -> pd.DataFrame:
        self._validate_input(df, ["close"])
        result = df.copy()
        
        for period in self.periods:
            col_name = f"sma_{period}"
            result[col_name] = df["close"].rolling(window=period).mean()
            
        return result
