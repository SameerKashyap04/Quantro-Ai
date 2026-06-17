"""
Quantro Personal AI — Indicator Calculator
"""
import pandas as pd

from packages.indicators.trend.ema import EMA
from packages.indicators.trend.sma import SMA
from packages.indicators.momentum.rsi import RSI
from packages.indicators.momentum.macd import MACD
from packages.indicators.momentum.stochastic_rsi import StochasticRSI
from packages.indicators.volatility.atr import ATR
from packages.indicators.volatility.bollinger import BollingerBands
from packages.indicators.volume.relative_volume import RelativeVolume
from packages.indicators.structure.pivot_points import PivotPoints


class IndicatorCalculator:
    """Batch calculator for applying all configured indicators to a DataFrame."""

    @staticmethod
    def calculate_all(df: pd.DataFrame) -> pd.DataFrame:
        """Run all standard indicators on the DataFrame."""
        if df.empty:
            return df
            
        result = df.copy()
        
        # Define indicators to run
        indicators = [
            EMA(periods=[20, 50, 100, 200]),
            SMA(periods=[20, 50, 200]),
            RSI(period=14),
            MACD(fast_period=12, slow_period=26, signal_period=9),
            StochasticRSI(period=14),
            ATR(period=14),
            BollingerBands(period=20, std_dev=2.0),
            RelativeVolume(period=20),
            PivotPoints()
        ]
        
        # Apply each indicator
        for indicator in indicators:
            try:
                # We calculate and then merge/update the result dataframe
                ind_result = indicator.calculate(result)
                # Find new columns
                new_cols = [c for c in ind_result.columns if c not in result.columns]
                for col in new_cols:
                    result[col] = ind_result[col]
            except Exception as e:
                # Log error in production, continue with others
                print(f"Error calculating {indicator.__class__.__name__}: {e}")
                
        return result
