import asyncio
import sys
import os

# Add project root to python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from sqlalchemy import text
from apps.api.database import async_session_factory

# Extracted from the provided Groww Holdings Images
HOLDINGS_DATA = [
    {"name": "ADANI POWER LTD", "symbol": "ADANIPOWER.NS", "isin": "INE814H01029", "qty": 48, "avg_price": 127.47, "close_price": 222.6},
    {"name": "BHARAT ELECTRONICS LTD", "symbol": "BEL.NS", "isin": "INE263A01024", "qty": 65, "avg_price": 275.08, "close_price": 407.55},
    {"name": "BHARTI AIRTEL LIMITED", "symbol": "BHARTIARTL.NS", "isin": "INE397D01024", "qty": 5, "avg_price": 1840.75, "close_price": 1853.0},
    {"name": "BILLIONBRAINS GARAGE VN L", "symbol": "ATHER.NS", "isin": "INE0HOQ01053", "qty": 4, "avg_price": 158.67, "close_price": 199.68},
    {"name": "CG POWER AND IND SOL LTD", "symbol": "CGPOWER.NS", "isin": "INE067A01029", "qty": 16, "avg_price": 649.95, "close_price": 940.7},
    {"name": "EPACK PREFAB TECHN LTD", "symbol": "EPACK.NS", "isin": "INE0MLS01022", "qty": 10, "avg_price": 278.48, "close_price": 249.12},
    {"name": "HDB FINANCIAL SERVICES L", "symbol": "HDB.NS", "isin": "INE756I01012", "qty": 30, "avg_price": 690.0, "close_price": 709.55},
    {"name": "NETWEB TECH INDIA LTD", "symbol": "NETWEB.NS", "isin": "INE0NT901020", "qty": 9, "avg_price": 3217.49, "close_price": 4884.4},
    {"name": "PSP PROJECTS LIMITED", "symbol": "PSPPROJECT.NS", "isin": "INE488V01015", "qty": 5, "avg_price": 937.65, "close_price": 907.8},
    {"name": "STATE BANK OF INDIA", "symbol": "SBIN.NS", "isin": "INE062A01020", "qty": 11, "avg_price": 801.65, "close_price": 1015.3},
    {"name": "VEDANTA ALUMINIUM METAL L", "symbol": "VEDAL.NS", "isin": "INE1CDF01017", "qty": 12, "avg_price": 29.3, "close_price": 471.11},
    {"name": "VEDANTA IRON AND STEEL L", "symbol": "VEDIS.NS", "isin": "INE1CLE01013", "qty": 12, "avg_price": 27.83, "close_price": 22.11},
    {"name": "VEDANTA LIMITED", "symbol": "VEDL.NS", "isin": "INE205A01025", "qty": 12, "avg_price": 214.54, "close_price": 299.95},
    {"name": "VEDANTA OIL AND GAS LTD", "symbol": "VEDOG.NS", "isin": "INE704J01044", "qty": 12, "avg_price": 88.08, "close_price": 34.3},
    {"name": "VEDANTA POWER LIMITED", "symbol": "VEDPL.NS", "isin": "INE694L01019", "qty": 12, "avg_price": 50.13, "close_price": 40.0},
]

async def seed_holdings():
    print("Connecting to database and mapping manual holdings...")
    async with async_session_factory() as session:
        for item in HOLDINGS_DATA:
            # 1. Insert into stocks if missing
            insert_stock_sql = text("""
                INSERT INTO stocks (symbol, name, sector, is_index, is_etf, is_active)
                VALUES (:symbol, :name, 'Unknown', FALSE, FALSE, TRUE)
                ON CONFLICT (symbol) DO NOTHING;
            """)
            await session.execute(insert_stock_sql, {"symbol": item["symbol"], "name": item["name"]})
            
            # Get stock ID
            stock_id_res = await session.execute(
                text("SELECT id FROM stocks WHERE symbol = :symbol"), 
                {"symbol": item["symbol"]}
            )
            stock_id = stock_id_res.scalar()
            
            if not stock_id:
                print(f"Failed to find or insert stock: {item['symbol']}")
                continue
                
            # 2. Upsert into portfolio_holdings
            qty = item["qty"]
            avg_price = item["avg_price"]
            current_price = item["close_price"]
            invested_value = qty * avg_price
            current_value = qty * current_price
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
                "qty": qty,
                "avg_price": avg_price,
                "current_price": current_price,
                "invested": invested_value,
                "current_val": current_value,
                "pnl": pnl,
                "pnl_pct": pnl_pct
            })
            
        await session.commit()
        print(f"✅ Successfully seeded {len(HOLDINGS_DATA)} holdings from screenshots!")

if __name__ == "__main__":
    asyncio.run(seed_holdings())
