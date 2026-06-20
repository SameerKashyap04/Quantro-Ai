"""
Quantro Personal AI — Signal Strategies
"""
import pandas as pd
from typing import Dict, Any, List

from services.ai_engine.predictor import AIPredictor
from services.ai_engine.regime import MarketRegimeDetector


class HybridStrategy:
    """Combines Technical Indicators and AI Predictions."""

    def __init__(self, predictor: AIPredictor):
        self.predictor = predictor

    def evaluate(self, df: pd.DataFrame, current_regime: str, news_data: List[Dict] = None, fund_data: dict = None) -> Dict[str, Any]:
        """Evaluate a stock's data to generate a signal."""
        if df.empty or len(df) < 2:
            return {"signal_type": "HOLD", "confidence": 0}
            
        latest = df.iloc[-1]
        prev = df.iloc[-2]
        
        # 1. Technical Screen
        tech_score = 50  # Start neutral
        
        # MACD logic (Trend)
        if 'macd' in latest and 'macd_signal' in latest:
            # Crossover gives strong points
            if prev['macd'] <= prev['macd_signal'] and latest['macd'] > latest['macd_signal']:
                tech_score += 30
            elif prev['macd'] >= prev['macd_signal'] and latest['macd'] < latest['macd_signal']:
                tech_score -= 30
            # Sustained trend gives smaller points
            elif latest['macd'] > latest['macd_signal']:
                tech_score += 15
            elif latest['macd'] < latest['macd_signal']:
                tech_score -= 15
                
        # RSI Check (Momentum)
        if 'rsi_14' in latest:
            rsi = latest['rsi_14']
            if rsi < 30: # Oversold
                tech_score += 25
            elif rsi > 70: # Overbought
                tech_score -= 25
            elif rsi > 50:
                tech_score += 10
            else:
                tech_score -= 10
                
        # Regime alignment
        if current_regime == "bull":
            tech_score += 15
        elif current_regime == "bear":
            tech_score -= 15
            
        # Determine tech_signal based on score
        tech_score = max(0, min(100, tech_score)) # Clamp between 0-100
        
        if tech_score >= 70:
            tech_signal = "BUY"
        elif tech_score <= 30:
            tech_signal = "SELL"
        else:
            tech_signal = "HOLD"
            
        # 2. AI Prediction
        # For a single stock, we pass the df to predictor
        ai_signals = self.predictor.generate_signals(df, news_data, fund_data)
        
        if not ai_signals:
            return {
                "signal_type": tech_signal if tech_score >= 50 else "HOLD",
                "confidence": tech_score,
                "strategy_name": "Technical_Only"
            }
            
        ai_signal = ai_signals[0]
        
        # 3. Combine
        final_signal = "HOLD"
        final_confidence = 0
        
        is_contradiction = (tech_signal == "BUY" and ai_signal['signal_type'] == "SELL") or (tech_signal == "SELL" and ai_signal['signal_type'] == "BUY")
        
        if is_contradiction:
            # Contradicting signals, default to HOLD
            final_signal = "HOLD"
            final_confidence = abs(tech_score - ai_signal['confidence']) / 2
        elif tech_signal == ai_signal['signal_type'] and tech_signal != "HOLD":
            # Strong confluence
            final_signal = tech_signal
            tech_confidence = (100 - tech_score) if tech_signal == "SELL" else tech_score
            final_confidence = (tech_confidence + ai_signal['confidence']) / 2
        elif ai_signal['signal_type'] != "HOLD" and ai_signal['confidence'] > 75:
            # AI override if very confident (and no strict contradiction)
            final_signal = ai_signal['signal_type']
            final_confidence = ai_signal['confidence'] * 0.85
        elif tech_signal == "BUY" and tech_score >= 70:
            # Technical override if very strong (and no strict contradiction)
            final_signal = "BUY"
            final_confidence = tech_score * 0.85
        elif tech_signal == "SELL" and tech_score <= 30:
            final_signal = "SELL"
            final_confidence = (100 - tech_score) * 0.85
            
        return {
            "signal_type": final_signal,
            "confidence": float(round(final_confidence, 2)),
            "strategy_name": "Hybrid_V1",
            "ai_bullish_prob": float(ai_signal.get('ai_bullish_prob')) if ai_signal.get('ai_bullish_prob') is not None else None,
            "ai_bearish_prob": float(ai_signal.get('ai_bearish_prob')) if ai_signal.get('ai_bearish_prob') is not None else None,
            "stop_loss_pct": float(ai_signal.get('stop_loss_pct')) if ai_signal.get('stop_loss_pct') is not None else None,
            "target_pct": float(ai_signal.get('target_pct')) if ai_signal.get('target_pct') is not None else None,
            "holding_period_days": ai_signal.get('holding_period_days'),
            "reasoning": {
                "tech_signal": tech_signal,
                "tech_score": tech_score,
                "ai_signal": ai_signal['signal_type'],
                "ai_confidence": ai_signal['confidence'],
                "current_price": ai_signal.get("reasoning", {}).get("current_price"),
                "target_price": ai_signal.get("reasoning", {}).get("target_price"),
                "stop_loss_price": ai_signal.get("reasoning", {}).get("stop_loss_price"),
                "recent_headlines": ai_signal.get("reasoning", {}).get("recent_headlines", []),
                "fundamentals": ai_signal.get("reasoning", {}).get("fundamentals", {})
            }
        }
