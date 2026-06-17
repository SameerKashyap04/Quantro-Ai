"""
Quantro Personal AI — AI Trainer
"""
import logging
import pandas as pd
from typing import List
from sklearn.metrics import accuracy_score, classification_report

from services.ai_engine.features import FeatureEngineer
from services.ai_engine.models import AIModelManager

logger = logging.getLogger(__name__)


class ModelTrainer:
    """Trains the ML models on historical data."""

    def __init__(self, model_manager: AIModelManager):
        self.model_manager = model_manager
        self.feature_cols = [
            'return_1d', 'return_5d', 'return_20d', 
            'dist_sma20', 'dist_ema50', 'atr_normalized', 
            'bb_position', 'rsi_14', 'macd', 'macd_hist'
        ]

    def train_model(self, data: pd.DataFrame, model_name: str) -> dict:
        """
        Train a model on provided historical dataframe.
        Expected: A single DataFrame with multiple stocks concatenated.
        """
        logger.info(f"Starting training for model '{model_name}'...")
        
        # 1. Feature Engineering
        features_df = FeatureEngineer.create_features(data)
        labeled_df = FeatureEngineer.create_labels(features_df)
        
        # Keep only required columns
        valid_cols = [col for col in self.feature_cols if col in labeled_df.columns]
        if not valid_cols:
            raise ValueError("No valid feature columns found in data.")
            
        X = labeled_df[valid_cols]
        y = labeled_df['target']
        
        # Train-Test Split (temporal)
        # Assuming data is sorted by date
        split_idx = int(len(X) * 0.8)
        X_train, X_test = X.iloc[:split_idx], X.iloc[split_idx:]
        y_train, y_test = y.iloc[:split_idx], y.iloc[split_idx:]
        
        logger.info(f"Training set: {len(X_train)} samples. Test set: {len(X_test)} samples.")
        
        # 2. Train Model
        model = self.model_manager.get_base_model("rf")
        model.fit(X_train, y_train)
        
        # 3. Evaluate
        preds = model.predict(X_test)
        acc = accuracy_score(y_test, preds)
        logger.info(f"Model accuracy on test set: {acc:.4f}")
        
        # 4. Save
        self.model_manager.save_model(model, model_name)
        
        return {
            "model_name": model_name,
            "accuracy": acc,
            "samples": len(X),
            "features_used": valid_cols
        }
