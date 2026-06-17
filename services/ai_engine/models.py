"""
Quantro Personal AI — AI Models
"""
import joblib
import os
import logging
from typing import Any

# We use scikit-learn for baseline models.
# In a real setup, this might be XGBoost, LightGBM, or PyTorch.
from sklearn.ensemble import RandomForestClassifier

logger = logging.getLogger(__name__)


class AIModelManager:
    """Manages saving, loading, and configuring ML models."""

    def __init__(self, model_dir: str = "/tmp/models"):
        self.model_dir = model_dir
        os.makedirs(self.model_dir, exist_ok=True)

    def get_base_model(self, model_type: str = "rf") -> Any:
        """Get an untrained model instance."""
        if model_type == "rf":
            return RandomForestClassifier(
                n_estimators=100,
                max_depth=10,
                random_state=42,
                class_weight="balanced",
                n_jobs=-1
            )
        else:
            raise ValueError(f"Unknown model type: {model_type}")

    def save_model(self, model: Any, name: str) -> str:
        """Save a trained model to disk."""
        path = os.path.join(self.model_dir, f"{name}.joblib")
        joblib.dump(model, path)
        logger.info(f"Model saved to {path}")
        return path

    def load_model(self, name: str) -> Any:
        """Load a trained model from disk."""
        path = os.path.join(self.model_dir, f"{name}.joblib")
        if not os.path.exists(path):
            raise FileNotFoundError(f"Model file not found: {path}")
        logger.info(f"Model loaded from {path}")
        return joblib.load(path)
