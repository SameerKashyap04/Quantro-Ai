"""
Quantro Personal AI — Regime Detection
"""
import pandas as pd
import numpy as np


class MarketRegimeDetector:
    """Determines the current overall market regime (Bull/Bear/Sideways)."""

    @staticmethod
    def detect_regime(nifty_df: pd.DataFrame) -> dict:
        """
        Detect regime based on NIFTY 50 data.
        Needs at least 200 days of data for the 200 SMA.
        """
        if len(nifty_df) < 200:
            return {"regime": "unknown", "confidence": 0, "nifty_trend": "unknown"}

        df = nifty_df.copy()
        
        # Calculate moving averages
        df['sma_50'] = df['close'].rolling(window=50).mean()
        df['sma_200'] = df['close'].rolling(window=200).mean()
        
        latest = df.iloc[-1]
        
        # Basic Price vs MA rules
        price = latest['close']
        sma50 = latest['sma_50']
        sma200 = latest['sma_200']
        
        regime = "sideways"
        confidence = 0.5
        trend = "flat"
        
        if price > sma50 and sma50 > sma200:
            regime = "bull"
            trend = "up"
            confidence = 0.8
        elif price < sma50 and sma50 < sma200:
            regime = "bear"
            trend = "down"
            confidence = 0.8
        elif price > sma200 and price < sma50:
            regime = "sideways"
            trend = "consolidation_bullish"
            confidence = 0.6
        elif price < sma200 and price > sma50:
            regime = "sideways"
            trend = "consolidation_bearish"
            confidence = 0.6
            
        return {
            "regime": regime,
            "confidence": confidence,
            "nifty_trend": trend
        }
