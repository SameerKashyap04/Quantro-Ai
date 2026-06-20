"""
Quantro Personal AI — Signals Repository
Database queries for signals.
"""
from typing import Optional
from uuid import UUID
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession


class SignalRepository:
    """Data access layer for signals."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_latest_signals(
        self,
        signal_type: Optional[str] = None,
        min_confidence: Optional[float] = None,
        risk_level: Optional[str] = None,
        strategy_name: Optional[str] = None,
        symbols: Optional[list[str]] = None,
        exclude_symbols: Optional[list[str]] = None,
        limit: int = 50,
    ) -> list[dict]:
        """Get latest active signals with stock info."""
        query = """
            SELECT s.*, st.symbol, st.name, st.sector
            FROM signals s
            JOIN stocks st ON s.stock_id = st.id
            WHERE s.is_active = true
        """
        params: dict = {}

        if signal_type:
            query += " AND s.signal_type = :signal_type"
            params["signal_type"] = signal_type.upper()
        if min_confidence:
            query += " AND s.confidence >= :min_confidence"
            params["min_confidence"] = min_confidence
        if risk_level:
            query += " AND s.risk_level = :risk_level"
            params["risk_level"] = risk_level
        if strategy_name:
            query += " AND s.strategy_name = :strategy_name"
            params["strategy_name"] = strategy_name
        if symbols:
            query += " AND st.symbol = ANY(:symbols)"
            params["symbols"] = symbols
        if exclude_symbols:
            query += " AND st.symbol != ALL(:exclude_symbols)"
            params["exclude_symbols"] = exclude_symbols

        query += " ORDER BY s.confidence DESC, s.created_at DESC LIMIT :limit"
        params["limit"] = limit

        result = await self.db.execute(text(query), params)
        return [dict(row._mapping) for row in result.fetchall()]

    async def get_signals_by_symbol(self, symbol: str, limit: int = 20) -> list[dict]:
        """Get signal history for a specific stock."""
        result = await self.db.execute(
            text("""
                SELECT s.*, st.symbol, st.name
                FROM signals s
                JOIN stocks st ON s.stock_id = st.id
                WHERE st.symbol = :symbol
                ORDER BY s.created_at DESC
                LIMIT :limit
            """),
            {"symbol": symbol.upper(), "limit": limit},
        )
        return [dict(row._mapping) for row in result.fetchall()]

    async def create_signal(self, signal_data: dict) -> dict:
        """Insert a new signal."""
        result = await self.db.execute(
            text("""
                INSERT INTO signals (stock_id, signal_type, confidence, stop_loss_pct,
                    target_pct, risk_level, strategy_name, reasoning_json,
                    ai_bullish_prob, ai_bearish_prob, holding_period_days)
                VALUES (:stock_id, :signal_type, :confidence, :stop_loss_pct,
                    :target_pct, :risk_level, :strategy_name, :reasoning_json,
                    :ai_bullish_prob, :ai_bearish_prob, :holding_period_days)
                RETURNING *
            """),
            signal_data,
        )
        row = result.fetchone()
        return dict(row._mapping) if row else {}

    async def deactivate_old_signals(self, stock_id: UUID) -> None:
        """Set is_active=false for previous signals of a stock."""
        await self.db.execute(
            text("UPDATE signals SET is_active = false WHERE stock_id = :stock_id"),
            {"stock_id": stock_id}
        )

    async def delete_old_signals(self, days_kept: int = 2) -> int:
        """Delete signals older than X days to prevent database bloat."""
        res = await self.db.execute(
            text("DELETE FROM signals WHERE created_at < NOW() - make_interval(days => :days)"),
            {"days": days_kept}
        )
        return res.rowcount
