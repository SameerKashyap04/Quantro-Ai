"""
Quantro Personal AI — Bollinger Bands Indicator
"""
import pandas as pd
from packages.indicators.base import BaseIndicator


class BollingerBands(BaseIndicator):
    """Bollinger Bands."""

    def __init__(self, period: int = 20, std_dev: float = 2.0):
        self.period = period
        self.std_dev = std_dev

    def calculate(self, df: pd.DataFrame) -> pd.DataFrame:
        self._validate_input(df, ["close"])
        result = df.copy()
        
        sma = df["close"].rolling(window=self.period).mean()
        std = df["close"].rolling(window=self.period).std()
        
        result["bb_upper"] = sma + (std * self.std_dev)
        result["bb_lower"] = sma - (std * self.std_dev)
        result["bb_middle"] = sma
        result["bb_width"] = (result["bb_upper"] - result["bb_lower"]) / result["bb_middle"]
        
        return result
