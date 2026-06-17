"""
Quantro Personal AI — AI Feature Engineering
"""
import pandas as pd
import numpy as np


class FeatureEngineer:
    """Prepares features from OHLCV and indicator data for the ML models."""

    @staticmethod
    def create_features(df: pd.DataFrame) -> pd.DataFrame:
        """Create ML features from raw data."""
        if df.empty:
            return df
            
        features = df.copy()
        
        # 1. Price Returns (Momentum features)
        features['return_1d'] = features['close'].pct_change()
        features['return_5d'] = features['close'].pct_change(5)
        features['return_20d'] = features['close'].pct_change(20)
        
        # 2. Distance from Moving Averages
        if 'sma_20' in features.columns:
            features['dist_sma20'] = (features['close'] - features['sma_20']) / features['sma_20']
        if 'ema_50' in features.columns:
            features['dist_ema50'] = (features['close'] - features['ema_50']) / features['ema_50']
            
        # 3. Volatility Features (Normalized ATR)
        if 'atr_14' in features.columns:
            features['atr_normalized'] = features['atr_14'] / features['close']
            
        # 4. Bollinger Band Position (0 = lower band, 1 = upper band)
        if 'bb_upper' in features.columns and 'bb_lower' in features.columns:
            bb_range = features['bb_upper'] - features['bb_lower']
            # Avoid division by zero
            features['bb_position'] = np.where(bb_range == 0, 0.5, 
                                             (features['close'] - features['bb_lower']) / bb_range)
            
        # Drop rows with NaNs caused by lookbacks
        return features.dropna()

    @staticmethod
    def create_labels(df: pd.DataFrame, horizon: int = 5, threshold: float = 0.02) -> pd.DataFrame:
        """
        Create target labels for classification.
        horizon: number of days ahead to look.
        threshold: minimum % return required to classify as BUY (1).
        -1: SELL, 0: HOLD, 1: BUY
        """
        if df.empty:
            return df
            
        labeled = df.copy()
        
        # Future return
        future_return = labeled['close'].shift(-horizon) / labeled['close'] - 1
        
        # Classification
        conditions = [
            (future_return >= threshold),
            (future_return <= -threshold)
        ]
        choices = [1, -1]
        
        labeled['target'] = np.select(conditions, choices, default=0)
        
        # The last 'horizon' rows will have NaN future returns, so drop them
        return labeled.dropna(subset=['target'])
