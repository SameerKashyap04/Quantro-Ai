"""
Quantro Personal AI — Backtest Engine
"""
import logging
import pandas as pd
from typing import Dict, Any

from services.backtest_engine.simulator import BacktestSimulator
from services.backtest_engine.evaluator import BacktestEvaluator
from services.signal_engine.strategies import HybridStrategy

logger = logging.getLogger(__name__)


class BacktestEngine:
    """Orchestrates historical backtesting over market data."""

    def __init__(self, strategy, initial_capital: float = 100000.0):
        self.strategy = strategy
        self.initial_capital = initial_capital

    def run(self, historical_data: Dict[str, pd.DataFrame]) -> Dict[str, Any]:
        """
        Run the backtest loop.
        historical_data: Dict of DataFrames per symbol, sorted chronologically.
        """
        logger.info("Starting backtest run...")
        
        simulator = BacktestSimulator(self.initial_capital)
        
        # In a real implementation, we would iterate day by day (event-driven)
        # or use vectorized backtesting.
        # This is a simplified event loop representation.
        
        # Extract a unified timeline
        all_dates = set()
        for df in historical_data.values():
            all_dates.update(df['timestamp'].tolist())
        timeline = sorted(list(all_dates))
        
        for date in timeline:
            current_prices = {}
            
            for symbol, df in historical_data.items():
                # Get data up to this date
                mask = df['timestamp'] <= date
                df_slice = df[mask]
                
                if df_slice.empty:
                    continue
                    
                latest_row = df_slice.iloc[-1]
                current_price = latest_row['close']
                current_prices[symbol] = current_price
                
                # Check for signals if we have enough data
                if len(df_slice) > 50:
                    signal = self.strategy.evaluate(df_slice, current_regime="unknown")
                    
                    if signal["signal_type"] == "BUY":
                        # Simple logic: Buy 10 shares
                        simulator.execute_buy(date, symbol, current_price, 10)
                    elif signal["signal_type"] == "SELL":
                        # Sell all holdings of this symbol
                        if symbol in simulator.positions:
                            qty = simulator.positions[symbol]["quantity"]
                            simulator.execute_sell(date, symbol, current_price, qty)
                            
            # End of day mark to market
            simulator.mark_to_market(date, current_prices)

        # Evaluate Results
        metrics = BacktestEvaluator.evaluate(simulator.trade_history, simulator.equity_curve)
        
        logger.info(f"Backtest complete. Final Capital: {metrics.get('final_capital')}")
        
        return {
            "metrics": metrics,
            "equity_curve": simulator.equity_curve,
            "trade_history": simulator.trade_history
        }
