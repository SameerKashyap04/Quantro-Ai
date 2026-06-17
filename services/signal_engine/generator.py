"""
Quantro Personal AI — Signal Generator
"""
import logging
import asyncio
from typing import List, Dict
import pandas as pd

from services.signal_engine.strategies import HybridStrategy
from services.signal_engine.filter import SignalFilter
from services.ai_engine.predictor import AIPredictor
from services.ai_engine.models import AIModelManager
from apps.api.signals.repository import SignalRepository

logger = logging.getLogger(__name__)


class SignalGenerator:
    """Orchestrates signal generation across the market universe."""

    def __init__(self, db_session, risk_settings: dict):
        self.db = db_session
        self.signal_repo = SignalRepository(self.db)
        self.filter = SignalFilter(risk_settings)
        
        # Init AI
        self.model_manager = AIModelManager()
        self.predictor = AIPredictor(self.model_manager)
        self.strategy = HybridStrategy(self.predictor)

    async def generate_for_market(self, market_data_map: Dict[str, pd.DataFrame], current_regime: str, news_data_map: Dict[str, List[Dict]] = None, fundamental_data_map: Dict[str, dict] = None):
        """
        Generate signals for all provided stocks.
        market_data_map: { "uuid-string": dataframe }
        news_data_map: { "uuid-string": [news items] }
        fundamental_data_map: { "uuid-string": dict_of_fundamentals }
        """
        logger.info(f"Generating signals for {len(market_data_map)} stocks. Regime: {current_regime}")
        
        valid_signals = []
        
        for stock_id, df in market_data_map.items():
            try:
                # 1. Evaluate Strategy
                news_data = news_data_map.get(stock_id) if news_data_map else None
                fund_data = fundamental_data_map.get(stock_id) if fundamental_data_map else None
                raw_signal = self.strategy.evaluate(df, current_regime, news_data, fund_data)
                
                logger.info(f"[{stock_id}] Raw Signal: {raw_signal}")
                if raw_signal["signal_type"] == "HOLD":
                    continue
                    
                # 2. Filter
                passes = self.filter.passes_filter(raw_signal, current_regime)
                logger.info(f"[{stock_id}] Filter passes: {passes}")
                if passes:
                    raw_signal["stock_id"] = stock_id
                    valid_signals.append(raw_signal)
                    
            except Exception as e:
                logger.error(f"Error generating signal for {stock_id}: {e}")
                import traceback
                logger.error(traceback.format_exc())
                
        # 3. Rank Signals (Confidence desc)
        valid_signals.sort(key=lambda x: x["confidence"], reverse=True)
        
        # 4. Save to DB
        await self._save_signals(valid_signals)
        
        logger.info(f"Generated {len(valid_signals)} valid signals.")
        return valid_signals

    async def _save_signals(self, signals: List[Dict]):
        """Save signals to database and deactivate old ones."""
        for sig in signals:
            try:
                # Deactivate old signals for this stock
                await self.signal_repo.deactivate_old_signals(sig["stock_id"])
                
                import json
                # Prepare for insert
                sig_data = {
                    "stock_id": sig["stock_id"],
                    "signal_type": sig["signal_type"],
                    "confidence": sig["confidence"],
                    "stop_loss_pct": sig.get("stop_loss_pct"),
                    "target_pct": sig.get("target_pct"),
                    "risk_level": "Medium", # Compute dynamically later
                    "strategy_name": sig["strategy_name"],
                    "reasoning_json": json.dumps(sig.get("reasoning", {})),
                    "ai_bullish_prob": sig.get("ai_bullish_prob"),
                    "ai_bearish_prob": sig.get("ai_bearish_prob"),
                    "holding_period_days": sig.get("holding_period_days")
                }
                
                await self.signal_repo.create_signal(sig_data)
            except Exception as e:
                logger.error(f"Failed to save signal for {sig['stock_id']}: {e}")
