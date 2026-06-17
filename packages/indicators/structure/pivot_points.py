"""
Quantro Personal AI — Pivot Points Indicator
"""
import pandas as pd
from packages.indicators.base import BaseIndicator


class PivotPoints(BaseIndicator):
    """Standard Pivot Points."""

    def calculate(self, df: pd.DataFrame) -> pd.DataFrame:
        self._validate_input(df, ["high", "low", "close"])
        result = df.copy()
        
        # Use previous day's high, low, close
        prev_h = df["high"].shift(1)
        prev_l = df["low"].shift(1)
        prev_c = df["close"].shift(1)
        
        result["pivot"] = (prev_h + prev_l + prev_c) / 3
        result["r1"] = (2 * result["pivot"]) - prev_l
        result["s1"] = (2 * result["pivot"]) - prev_h
        result["r2"] = result["pivot"] + (prev_h - prev_l)
        result["s2"] = result["pivot"] - (prev_h - prev_l)
        
        return result
