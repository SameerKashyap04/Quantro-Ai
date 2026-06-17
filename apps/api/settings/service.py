"""
Quantro Personal AI — Settings Service
"""
import json
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from apps.api.core.exceptions import NotFoundError


class SettingsService:
    """Service to manage system and risk settings stored in the database."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_all_settings(self) -> dict:
        """Get all system and risk settings."""
        # Get system settings
        sys_res = await self.db.execute(text("SELECT key, value FROM system_settings"))
        system_settings = {row[0]: json.loads(row[1]) if isinstance(row[1], str) else row[1] for row in sys_res.fetchall()}

        # Clean up string quotes from JSONB extraction if any
        for k, v in system_settings.items():
            if isinstance(v, str) and v.startswith('"') and v.endswith('"'):
                system_settings[k] = v.strip('"')

        # Get risk config
        risk_res = await self.db.execute(text("SELECT * FROM risk_config LIMIT 1"))
        risk_row = risk_res.fetchone()
        risk_config = dict(risk_row._mapping) if risk_row else {}
        
        # Remove DB specific fields
        risk_config.pop("id", None)
        risk_config.pop("updated_at", None)
        
        # Convert Decimals to float
        for k, v in risk_config.items():
            if hasattr(v, "to_eng_string"): # It's a Decimal
                risk_config[k] = float(v)

        return {
            "system": system_settings,
            "risk": risk_config
        }

    async def update_system_settings(self, updates: dict) -> None:
        """Update system settings (key-value)."""
        for key, value in updates.items():
            await self.db.execute(
                text("""
                    INSERT INTO system_settings (key, value, updated_at) 
                    VALUES (:key, :value::jsonb, NOW())
                    ON CONFLICT (key) DO UPDATE SET value = :value::jsonb, updated_at = NOW()
                """),
                {"key": key, "value": json.dumps(value)}
            )

    async def update_risk_settings(self, updates: dict) -> None:
        """Update risk configuration."""
        set_clauses = [f"{k} = :{k}" for k in updates.keys()]
        set_clauses.append("updated_at = NOW()")
        
        await self.db.execute(
            text(f"""
                UPDATE risk_config 
                SET {', '.join(set_clauses)}
            """),
            updates
        )
