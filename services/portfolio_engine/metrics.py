"""
Quantro Personal AI — Portfolio Metrics
"""
from typing import List, Dict
import pandas as pd
import numpy as np


class PortfolioMetrics:
    """Calculates advanced portfolio metrics over time."""

    @staticmethod
    def calculate_cagr(start_value: float, end_value: float, years: float) -> float:
        """Calculate Compound Annual Growth Rate."""
        if start_value <= 0 or years <= 0:
            return 0.0
        return ((end_value / start_value) ** (1 / years) - 1) * 100

    @staticmethod
    def calculate_sharpe_ratio(returns: pd.Series, risk_free_rate: float = 0.05, periods: int = 252) -> float:
        """Calculate annualized Sharpe Ratio."""
        if len(returns) < 2:
            return 0.0
            
        mean_return = returns.mean()
        std_dev = returns.std()
        
        if std_dev == 0:
            return 0.0
            
        daily_rf = risk_free_rate / periods
        sharpe = (mean_return - daily_rf) / std_dev
        return sharpe * np.sqrt(periods)

    @staticmethod
    def calculate_max_drawdown(equity_curve: pd.Series) -> float:
        """Calculate Maximum Drawdown from an equity curve series."""
        if equity_curve.empty:
            return 0.0
            
        rolling_max = equity_curve.cummax()
        drawdown = (equity_curve - rolling_max) / rolling_max
        return abs(drawdown.min()) * 100
