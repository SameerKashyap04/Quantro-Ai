"""
Quantro Personal AI — Stochastic RSI Indicator
"""
import pandas as pd
from packages.indicators.base import BaseIndicator
from packages.indicators.momentum.rsi import RSI


class StochasticRSI(BaseIndicator):
    """Stochastic RSI."""

    def __init__(self, period: int = 14, smooth_k: int = 3, smooth_d: int = 3):
        self.period = period
        self.smooth_k = smooth_k
        self.smooth_d = smooth_d

    def calculate(self, df: pd.DataFrame) -> pd.DataFrame:
        self._validate_input(df, ["close"])
        
        # First calculate normal RSI
        rsi_indicator = RSI(period=self.period)
        result = rsi_indicator.calculate(df)
        
        rsi_col = f"rsi_{self.period}"
        
        # Calculate Stochastic of RSI
        stoch_rsi = (result[rsi_col] - result[rsi_col].rolling(window=self.period).min()) / \
                    (result[rsi_col].rolling(window=self.period).max() - result[rsi_col].rolling(window=self.period).min())
        
        result["stoch_rsi_k"] = stoch_rsi.rolling(window=self.smooth_k).mean() * 100
        result["stoch_rsi_d"] = result["stoch_rsi_k"].rolling(window=self.smooth_d).mean()
        
        return result
