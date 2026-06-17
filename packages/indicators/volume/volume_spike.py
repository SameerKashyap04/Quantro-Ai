"""
Quantro Personal AI — Volume Spike Indicator
"""
import pandas as pd
from packages.indicators.base import BaseIndicator


class VolumeSpike(BaseIndicator):
    """Volume Spike Detection."""

    def __init__(self, period: int = 20, threshold: float = 2.5):
        self.period = period
        self.threshold = threshold

    def calculate(self, df: pd.DataFrame) -> pd.DataFrame:
        self._validate_input(df, ["volume"])
        result = df.copy()
        
        avg_volume = df["volume"].rolling(window=self.period).mean()
        std_volume = df["volume"].rolling(window=self.period).std()
        
        spike_threshold = avg_volume + (std_volume * self.threshold)
        result["is_volume_spike"] = df["volume"] > spike_threshold
        
        return result
