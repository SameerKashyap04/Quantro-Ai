import asyncio
import sys
import os

# Add project root to python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from sqlalchemy import text
from apps.api.config import get_settings
from apps.api.database import async_session_factory
from packages.broker_adapters.groww.adapter import GrowwAdapter

async def sync_holdings_to_db(holdings: list):
    """
    Takes the holdings payload from GrowwAPI and upserts them into the local DB.
    Because the exact JSON format requires an active token to inspect, this uses
    a generic best-effort mapping that covers standard algorithmic broker responses.
    """
    async with async_session_factory() as session:
        for item in holdings:
            # Common key names across broker APIs
            symbol = item.get("symbol") or item.get("trading_symbol") or item.get("companyName")
            if not symbol:
                continue
                
            qty = item.get("quantity") or item.get("availableQty", 0)
            avg_price = item.get("average_price") or item.get("avgPrice", 0.0)
            current_price = item.get("current_price") or item.get("ltp", avg_price)
            
            # Map symbol to our DB (Appending .NS for Yahoo Finance compatibility if missing)
            if not symbol.endswith(".NS") and not symbol.endswith(".BO"):
                mapped_symbol = f"{symbol}.NS"
            else:
                mapped_symbol = symbol
                
            # 1. Ensure stock exists
            insert_stock_sql = text("""
                INSERT INTO stocks (symbol, name, sector, is_index, is_etf, is_active)
                VALUES (:symbol, :name, 'Unknown', FALSE, FALSE, TRUE)
                ON CONFLICT (symbol) DO NOTHING
                RETURNING id;
            """)
            await session.execute(insert_stock_sql, {"symbol": mapped_symbol, "name": symbol})
            
            # Get stock ID
            stock_id_res = await session.execute(
                text("SELECT id FROM stocks WHERE symbol = :symbol"), 
                {"symbol": mapped_symbol}
            )
            stock_id = stock_id_res.scalar()
            
            if not stock_id:
                continue
                
            # 2. Upsert into portfolio_holdings
            invested_value = float(qty) * float(avg_price)
            current_value = float(qty) * float(current_price)
            pnl = current_value - invested_value
            pnl_pct = (pnl / invested_value * 100) if invested_value > 0 else 0.0
            
            upsert_holdings_sql = text("""
                INSERT INTO portfolio_holdings (
                    stock_id, quantity, avg_buy_price, current_price, 
                    invested_value, current_value, pnl, pnl_pct, source
                ) VALUES (
                    :stock_id, :qty, :avg_price, :current_price,
                    :invested, :current_val, :pnl, :pnl_pct, 'groww'
                ) ON CONFLICT (stock_id, source) DO UPDATE SET
                    quantity = EXCLUDED.quantity,
                    avg_buy_price = EXCLUDED.avg_buy_price,
                    current_price = EXCLUDED.current_price,
                    invested_value = EXCLUDED.invested_value,
                    current_value = EXCLUDED.current_value,
                    pnl = EXCLUDED.pnl,
                    pnl_pct = EXCLUDED.pnl_pct,
                    updated_at = CURRENT_TIMESTAMP;
            """)
            
            await session.execute(upsert_holdings_sql, {
                "stock_id": stock_id,
                "qty": float(qty),
                "avg_price": float(avg_price),
                "current_price": float(current_price),
                "invested": invested_value,
                "current_val": current_value,
                "pnl": pnl,
                "pnl_pct": pnl_pct
            })
            
        await session.commit()
        print(f"✅ Successfully synced {len(holdings)} holdings to the local database.")

async def main():
    print("Initializing GrowwAdapter...")
    settings = get_settings()
    
    # Access token must be set in .env
    token = settings.groww_access_token or settings.broker_api_key
    adapter = GrowwAdapter(
        api_key=settings.groww_api_key or settings.broker_api_key,
        api_secret=settings.groww_api_secret or settings.broker_api_secret,
        access_token=token
    )
    
    print("Testing Authentication...")
    is_auth = await adapter.authenticate()
    if not is_auth:
        print("❌ Authentication failed. Check your GROWW_ACCESS_TOKEN.")
        return
        
    print("✅ Authenticated successfully.")
    
    print("Fetching Holdings...")
    holdings = await adapter.get_holdings()
    
    if not holdings:
        print("No holdings found or failed to fetch.")
    else:
        print(f"✅ Found {len(holdings) if isinstance(holdings, list) else 1} holdings.")
        await sync_holdings_to_db(holdings)

if __name__ == "__main__":
    asyncio.run(main())
