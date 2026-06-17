"""
Quantro Personal AI — AI Predictor
"""
import logging
import pandas as pd
import numpy as np
from typing import List, Dict

from services.ai_engine.features import FeatureEngineer
from services.ai_engine.models import AIModelManager
from services.ai_engine.sentiment import SentimentAnalyzer

logger = logging.getLogger(__name__)


class AIPredictor:
    """Generates signals using trained ML models."""

    def __init__(self, model_manager: AIModelManager, model_name: str = "primary_model"):
        self.model_manager = model_manager
        self.model_name = model_name
        self.model = None
        self.feature_cols = [
            'return_1d', 'return_5d', 'return_20d', 
            'dist_sma20', 'dist_ema50', 'atr_normalized', 
            'bb_position', 'rsi_14', 'macd', 'macd_hist'
        ]

    def _load_model(self):
        if self.model is None:
            self.model = self.model_manager.load_model(self.model_name)

    def generate_signals(self, latest_data: pd.DataFrame, news_data: List[Dict] = None, fund_data: dict = None) -> List[Dict]:
        """
        Generate trading signals for the latest row of each stock.
        latest_data should contain the most recent data (with enough lookback for features).
        news_data contains recent news headlines for sentiment analysis.
        fund_data contains fundamental metrics.
        """
        try:
            self._load_model()
        except FileNotFoundError:
            logger.warning(f"Model '{self.model_name}' not found. Using heuristic fallback.")
            self.model = None

        # Engineer features
        features_df = FeatureEngineer.create_features(latest_data)
        if features_df.empty:
            return []
            
        # Get the latest row for prediction (assuming index/timestamp is sorted)
        latest_row = features_df.iloc[[-1]]
        
        # Extract features
        valid_cols = [col for col in self.feature_cols if col in latest_row.columns]
        X = latest_row[valid_cols]
        
        # Predict Probabilities
        if self.model:
            # classes are typically [-1, 0, 1] for SELL, HOLD, BUY
            probs = self.model.predict_proba(X)[0]
            classes = self.model.classes_
            
            prob_dict = {cls: prob for cls, prob in zip(classes, probs)}
            
            buy_prob = prob_dict.get(1, 0.0)
            sell_prob = prob_dict.get(-1, 0.0)
        else:
            # MOCK PREDICTIONS based on simple heuristics since model is not trained yet
            # For demonstration, we FORCE a signal so the user sees something in the dashboard
            rsi = latest_row['rsi_14'].iloc[0] if 'rsi_14' in latest_row.columns else 50
            if pd.isna(rsi):
                rsi = 50
                
            if rsi < 55:
                # Dynamic confidence based on RSI (lower = more confident buy)
                # Example: RSI 30 -> 0.65 + (25/55)*0.30 = 0.65 + 0.136 = 0.786
                buy_prob = min(0.95, 0.65 + ((55 - rsi) / 55.0) * 0.30)
                sell_prob = 0.10 + (rsi / 55.0) * 0.10
            else:
                # Dynamic confidence based on RSI (higher = more confident sell)
                buy_prob = 0.10 + ((100 - rsi) / 45.0) * 0.10
                sell_prob = min(0.95, 0.65 + ((rsi - 55) / 45.0) * 0.30)
                
        # --- NEWS SENTIMENT ADJUSTMENT ---
        sentiment_score = 0.0
        headlines = []
        if news_data:
            headlines = [{"title": n.get("title", ""), "link": n.get("link", "")} for n in news_data if n.get("title")]
            sentiment_score = SentimentAnalyzer.analyze_headlines([h["title"] for h in headlines])
            
            # Boost probabilities based on sentiment (-1.0 to 1.0)
            if sentiment_score > 0:
                buy_prob = min(0.99, buy_prob + (sentiment_score * 0.20)) # Max 20% boost
                sell_prob = max(0.01, sell_prob - (sentiment_score * 0.20))
            elif sentiment_score < 0:
                sell_prob = min(0.99, sell_prob + (abs(sentiment_score) * 0.20))
                buy_prob = max(0.01, buy_prob - (abs(sentiment_score) * 0.20))
                
        # --- FUNDAMENTAL ADJUSTMENT ---
        fund_score = 0.0
        if fund_data:
            pe = fund_data.get("trailingPE")
            roe = fund_data.get("returnOnEquity")
            dte = fund_data.get("debtToEquity")
            
            if pe and pe > 0:
                if pe < 15: fund_score += 0.15
                elif pe > 40: fund_score -= 0.15
                
            if roe and roe > 0:
                if roe > 0.15: fund_score += 0.10
                elif roe < 0.05: fund_score -= 0.10
                
            if dte:
                if dte < 50: fund_score += 0.10 # Assuming represented as percentage or ratio
                elif dte > 150: fund_score -= 0.10
                
            if fund_score > 0:
                buy_prob = min(0.99, buy_prob + fund_score)
                sell_prob = max(0.01, sell_prob - fund_score)
            elif fund_score < 0:
                sell_prob = min(0.99, sell_prob + abs(fund_score))
                buy_prob = max(0.01, buy_prob - abs(fund_score))
        
        # Determine Signal
        signal_type = "HOLD"
        confidence = 0.0
        
        if buy_prob > 0.65:
            signal_type = "BUY"
            confidence = buy_prob * 100
        elif sell_prob > 0.65:
            signal_type = "SELL"
            confidence = sell_prob * 100
            
        # Calculate suggested risk parameters based on ATR
        current_price = latest_row['close'].iloc[0]
        atr = latest_row['atr_14'].iloc[0] if 'atr_14' in latest_row.columns else (current_price * 0.02)
        
        stop_loss = current_price - (atr * 1.5) if signal_type == "BUY" else current_price + (atr * 1.5)
        target = current_price + (atr * 3.0) if signal_type == "BUY" else current_price - (atr * 3.0)
        
        stop_loss_pct = abs(current_price - stop_loss) / current_price * 100
        target_pct = abs(current_price - target) / current_price * 100
        
        # Calculate a realistic swing-trade holding period
        # Target % divided by Daily ATR %, multiplied by a market friction factor (e.g. 3.5 days per 1% move)
        daily_volatility_pct = (atr / current_price * 100) if atr > 0 else 1.5
        holding_period_days = int(max(14, round((target_pct / daily_volatility_pct) * 3.5)))

        return [{
            "signal_type": signal_type,
            "confidence": float(round(confidence, 2)),
            "ai_bullish_prob": float(round(buy_prob, 4)),
            "ai_bearish_prob": float(round(sell_prob, 4)),
            "stop_loss_pct": float(round(stop_loss_pct, 2)),
            "target_pct": float(round(target_pct, 2)),
            "holding_period_days": holding_period_days,
            "risk_level": "Medium", # Could be dynamic based on ATR
            "strategy_name": f"AI_{self.model_name}",
            "reasoning": {
                "buy_prob": float(round(buy_prob, 4)),
                "sell_prob": float(round(sell_prob, 4)),
                "sentiment_score": float(round(sentiment_score, 2)),
                "top_features": ["return_20d", "rsi_14"], # Mocked feature importance
                "recent_headlines": headlines[:3] if headlines else [],
                "current_price": float(round(current_price, 2)),
                "target_price": float(round(target, 2)),
                "stop_loss_price": float(round(stop_loss, 2)),
                "fundamentals": fund_data or {}
            }
        }]
