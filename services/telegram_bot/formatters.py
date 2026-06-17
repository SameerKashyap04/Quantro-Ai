"""
Quantro Personal AI — Telegram Formatters
"""

class TelegramFormatter:
    """Helper methods to format messages nicely for Telegram."""

    @staticmethod
    def format_signal_alert(signal: dict) -> str:
        """Format a trading signal alert."""
        symbol = signal.get("symbol", "UNKNOWN")
        action = signal.get("signal_type", "HOLD")
        confidence = signal.get("confidence", 0)
        sl = signal.get("stop_loss_pct", "N/A")
        tgt = signal.get("target_pct", "N/A")
        
        emoji = "🟢" if action == "BUY" else "🔴"
        if action == "HOLD": emoji = "⚪"
        
        msg = f"{emoji} *NEW SIGNAL*: {symbol}\n\n"
        msg += f"Action: {action}\n"
        msg += f"Confidence: {confidence}%\n"
        msg += f"Stop Loss: {sl}%\n"
        msg += f"Target: {tgt}%\n"
        msg += f"Strategy: {signal.get('strategy_name', 'Unknown')}\n\n"
        
        ai_bull = signal.get("ai_bullish_prob")
        if ai_bull is not None:
            msg += f"🤖 AI Bull Prob: {ai_bull*100:.1f}%\n"
            
        return msg

    @staticmethod
    def format_portfolio_summary(summary: dict) -> str:
        """Format a daily portfolio summary."""
        val = summary.get("total_value", 0)
        pnl = summary.get("total_pnl", 0)
        pnl_pct = summary.get("total_pnl_pct", 0)
        dpnl = summary.get("daily_pnl", 0)
        
        emoji = "📈" if pnl >= 0 else "📉"
        
        msg = f"{emoji} *PORTFOLIO UPDATE*\n\n"
        msg += f"Value: ₹{val:,.2f}\n"
        msg += f"Total P&L: ₹{pnl:,.2f} ({pnl_pct:.2f}%)\n"
        msg += f"Day Change: ₹{dpnl:,.2f}\n"
        msg += f"Holdings: {summary.get('num_holdings', 0)}\n"
        
        return msg
        
    @staticmethod
    def format_error(error_msg: str) -> str:
        """Format an error alert."""
        return f"🚨 *SYSTEM ERROR*\n\n{error_msg}"
