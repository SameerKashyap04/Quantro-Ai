"""
Quantro Personal AI — Backtest Simulator
"""
import pandas as pd
from typing import Dict, Any, List

class BacktestSimulator:
    """Simulates market execution over historical data."""

    def __init__(self, initial_capital: float, slippage_pct: float = 0.001, commission: float = 20.0):
        self.initial_capital = initial_capital
        self.current_capital = initial_capital
        self.slippage_pct = slippage_pct
        self.commission = commission
        
        self.positions: Dict[str, Any] = {}
        self.trade_history: List[Dict[str, Any]] = []
        self.equity_curve: List[Dict[str, Any]] = []

    def execute_buy(self, date, symbol: str, price: float, quantity: int):
        """Simulate a BUY order."""
        executed_price = price * (1 + self.slippage_pct)
        cost = (executed_price * quantity) + self.commission
        
        if cost > self.current_capital:
            return False # Insufficient funds
            
        self.current_capital -= cost
        
        if symbol in self.positions:
            # Update average price
            old_qty = self.positions[symbol]["quantity"]
            old_price = self.positions[symbol]["avg_price"]
            new_qty = old_qty + quantity
            new_price = ((old_qty * old_price) + (quantity * executed_price)) / new_qty
            self.positions[symbol] = {"quantity": new_qty, "avg_price": new_price}
        else:
            self.positions[symbol] = {"quantity": quantity, "avg_price": executed_price}
            
        self.trade_history.append({
            "date": date, "symbol": symbol, "action": "BUY",
            "quantity": quantity, "price": executed_price, "commission": self.commission
        })
        return True

    def execute_sell(self, date, symbol: str, price: float, quantity: int):
        """Simulate a SELL order."""
        if symbol not in self.positions or self.positions[symbol]["quantity"] < quantity:
            return False # Cannot sell what we don't have
            
        executed_price = price * (1 - self.slippage_pct)
        revenue = (executed_price * quantity) - self.commission
        
        avg_price = self.positions[symbol]["avg_price"]
        pnl = (executed_price - avg_price) * quantity - self.commission
        
        self.current_capital += revenue
        self.positions[symbol]["quantity"] -= quantity
        
        if self.positions[symbol]["quantity"] == 0:
            del self.positions[symbol]
            
        self.trade_history.append({
            "date": date, "symbol": symbol, "action": "SELL",
            "quantity": quantity, "price": executed_price, 
            "commission": self.commission, "pnl": pnl
        })
        return True

    def mark_to_market(self, date, current_prices: Dict[str, float]):
        """Calculate total portfolio value at the end of a time step."""
        portfolio_value = self.current_capital
        for symbol, pos in self.positions.items():
            if symbol in current_prices:
                portfolio_value += pos["quantity"] * current_prices[symbol]
                
        self.equity_curve.append({
            "date": date,
            "equity": portfolio_value
        })
