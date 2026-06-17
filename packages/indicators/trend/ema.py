"""
Quantro Personal AI — EMA Indicator
"""
import pandas as pd
from packages.indicators.base import BaseIndicator


class EMA(BaseIndicator):
    """Exponential Moving Average."""

    def __init__(self, periods: list[int] = [20, 50, 100, 200]):
        self.periods = periods

    def calculate(self, df: pd.DataFrame) -> pd.DataFrame:
        self._validate_input(df, ["close"])
        result = df.copy()
        
        for period in self.periods:
            col_name = f"ema_{period}"
            result[col_name] = df["close"].ewm(span=period, adjust=False).mean()
            
        return result
