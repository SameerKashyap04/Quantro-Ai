"""
Quantro Personal AI — MACD Indicator
"""
import pandas as pd
from packages.indicators.base import BaseIndicator


class MACD(BaseIndicator):
    """Moving Average Convergence Divergence."""

    def __init__(self, fast_period: int = 12, slow_period: int = 26, signal_period: int = 9):
        self.fast_period = fast_period
        self.slow_period = slow_period
        self.signal_period = signal_period

    def calculate(self, df: pd.DataFrame) -> pd.DataFrame:
        self._validate_input(df, ["close"])
        result = df.copy()
        
        fast_ema = df["close"].ewm(span=self.fast_period, adjust=False).mean()
        slow_ema = df["close"].ewm(span=self.slow_period, adjust=False).mean()
        
        macd_line = fast_ema - slow_ema
        signal_line = macd_line.ewm(span=self.signal_period, adjust=False).mean()
        macd_hist = macd_line - signal_line
        
        result["macd"] = macd_line
        result["macd_signal"] = signal_line
        result["macd_hist"] = macd_hist
        
        return result
