"""
Quantro Personal AI — Backtest Evaluator
"""
import pandas as pd
from typing import List, Dict, Any

from services.portfolio_engine.metrics import PortfolioMetrics


class BacktestEvaluator:
    """Computes final metrics from a backtest simulation."""

    @staticmethod
    def evaluate(trade_history: List[Dict], equity_curve: List[Dict]) -> Dict[str, Any]:
        """Calculate performance metrics."""
        if not equity_curve:
            return {}
            
        df_equity = pd.DataFrame(equity_curve)
        start_equity = df_equity["equity"].iloc[0]
        end_equity = df_equity["equity"].iloc[-1]
        
        # Calculate timeframe in years for CAGR
        try:
            start_date = pd.to_datetime(df_equity["date"].iloc[0])
            end_date = pd.to_datetime(df_equity["date"].iloc[-1])
            days = (end_date - start_date).days
            years = max(days / 365.25, 0.01) # Avoid div 0
        except:
            years = 1.0

        cagr = PortfolioMetrics.calculate_cagr(start_equity, end_equity, years)
        max_dd = PortfolioMetrics.calculate_max_drawdown(df_equity["equity"])
        
        # Trade metrics
        df_trades = pd.DataFrame([t for t in trade_history if t["action"] == "SELL"])
        
        winning_trades = 0
        losing_trades = 0
        win_rate = 0.0
        avg_win = 0.0
        avg_loss = 0.0
        profit_factor = 0.0
        
        if not df_trades.empty and "pnl" in df_trades.columns:
            wins = df_trades[df_trades["pnl"] > 0]
            losses = df_trades[df_trades["pnl"] <= 0]
            
            winning_trades = len(wins)
            losing_trades = len(losses)
            total_closed = winning_trades + losing_trades
            
            win_rate = (winning_trades / total_closed * 100) if total_closed > 0 else 0
            
            gross_profit = wins["pnl"].sum()
            gross_loss = abs(losses["pnl"].sum())
            
            avg_win = wins["pnl"].mean() if winning_trades > 0 else 0
            avg_loss = losses["pnl"].mean() if losing_trades > 0 else 0
            
            profit_factor = (gross_profit / gross_loss) if gross_loss > 0 else float('inf')

        return {
            "initial_capital": start_equity,
            "final_capital": end_equity,
            "cagr": round(cagr, 2),
            "max_drawdown": round(max_dd, 2),
            "total_trades": len(trade_history),
            "winning_trades": winning_trades,
            "losing_trades": losing_trades,
            "win_rate": round(win_rate, 2),
            "profit_factor": round(profit_factor, 2) if profit_factor != float('inf') else 99.99,
            "avg_win": round(avg_win, 2),
            "avg_loss": round(avg_loss, 2)
        }
