"""
Quantro Personal AI — RSI Indicator
"""
import pandas as pd
import numpy as np
from packages.indicators.base import BaseIndicator


class RSI(BaseIndicator):
    """Relative Strength Index."""

    def __init__(self, period: int = 14):
        self.period = period

    def calculate(self, df: pd.DataFrame) -> pd.DataFrame:
        self._validate_input(df, ["close"])
        result = df.copy()
        
        delta = df["close"].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=self.period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=self.period).mean()
        
        # Avoid division by zero
        rs = np.where(loss == 0, 100, gain / loss)
        
        result[f"rsi_{self.period}"] = 100 - (100 / (1 + rs))
        
        return result
