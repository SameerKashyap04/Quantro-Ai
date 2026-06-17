"""
Quantro Personal AI — ATR Indicator
"""
import pandas as pd
import numpy as np
from packages.indicators.base import BaseIndicator


class ATR(BaseIndicator):
    """Average True Range."""

    def __init__(self, period: int = 14):
        self.period = period

    def calculate(self, df: pd.DataFrame) -> pd.DataFrame:
        self._validate_input(df, ["high", "low", "close"])
        result = df.copy()
        
        high_low = df["high"] - df["low"]
        high_close = np.abs(df["high"] - df["close"].shift())
        low_close = np.abs(df["low"] - df["close"].shift())
        
        ranges = pd.concat([high_low, high_close, low_close], axis=1)
        true_range = np.max(ranges, axis=1)
        
        result[f"atr_{self.period}"] = true_range.rolling(window=self.period).mean()
        
        return result
