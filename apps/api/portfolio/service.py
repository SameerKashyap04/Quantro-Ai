"""
Quantro Personal AI — Portfolio Service
"""
import math
from sqlalchemy.ext.asyncio import AsyncSession
import pandas as pd
import io

from apps.api.portfolio.repository import PortfolioRepository
from apps.api.market.repository import MarketRepository


class PortfolioService:
    """Portfolio analysis business logic."""

    def __init__(self, db: AsyncSession):
        self.repo = PortfolioRepository(db)
        self.market_repo = MarketRepository(db)
        self.db = db

    async def sync_live_prices(self, source: str = "groww") -> None:
        """Sync live prices from YFinance and update the portfolio."""
        from services.market_data.fetchers import YFinanceFetcher
        import asyncio
        from datetime import datetime, timezone
        
        holdings = await self.repo.get_holdings(source)
        if not holdings:
            return
            
        # Check if updated recently (within last 5 minutes)
        last_updated = holdings[0].get("updated_at")
        if last_updated:
            if isinstance(last_updated, str):
                from dateutil.parser import parse
                last_updated = parse(last_updated)
            now = datetime.now(timezone.utc)
            if last_updated.tzinfo is None:
                now = datetime.now()
            if (now - last_updated).total_seconds() < 300:
                return

        fetcher = YFinanceFetcher()
        
        async def fetch_and_update(h):
            symbol = h["symbol"]
            stock_id = h["stock_id"]
            price_data = await asyncio.to_thread(fetcher.fetch_latest_price, symbol, False)
            if price_data and price_data.get("price"):
                current_price = float(price_data["price"])
                quantity = float(h["quantity"])
                avg_buy_price = float(h["avg_buy_price"])
                
                current_value = quantity * current_price
                invested_value = float(h.get("invested_value") or (quantity * avg_buy_price))
                pnl = current_value - invested_value
                pnl_pct = (pnl / invested_value * 100) if invested_value > 0 else 0
                
                h_new = {
                    "stock_id": stock_id,
                    "quantity": quantity,
                    "avg_buy_price": avg_buy_price,
                    "current_price": current_price,
                    "invested_value": invested_value,
                    "current_value": current_value,
                    "pnl": pnl,
                    "pnl_pct": pnl_pct,
                    "source": h["source"]
                }
                await self.repo.upsert_holding(h_new)

        tasks = [fetch_and_update(h) for h in holdings]
        await asyncio.gather(*tasks, return_exceptions=True)
        await self.db.commit()

    async def get_holdings(self, source: str = "paper") -> list[dict]:
        """Get portfolio holdings with weights."""
        await self.sync_live_prices(source)
        holdings = await self.repo.get_holdings(source)
        total_value = sum(h.get("current_value") or 0 for h in holdings)
        for h in holdings:
            h["weight_pct"] = round(
                ((h.get("current_value") or 0) / total_value * 100) if total_value > 0 else 0, 2
            )
        return holdings

    async def upload_excel_holdings(self, file_bytes: bytes, source: str = "groww_excel") -> dict:
        """Parse an uploaded Excel file of holdings and upsert to database."""
        try:
            # First pass: find the header row (sometimes Groww exports have title rows)
            df_preview = pd.read_excel(io.BytesIO(file_bytes), header=None, nrows=50)
            header_row_idx = None
            for idx, row in df_preview.iterrows():
                row_str = " ".join([str(val).lower() for val in row.values])
                has_name = any(x in row_str for x in ['symbol', 'instrument', 'company', 'stock', 'name', 'asset', 'fund'])
                has_qty = any(x in row_str for x in ['qty', 'quantity', 'shares', 'balance', 'available', 'units'])
                has_price = any(x in row_str for x in ['price', 'cmp', 'ltp', 'cost', 'nav', 'avg'])
                if has_name and has_qty and has_price:
                    header_row_idx = idx
                    break
                    
            if header_row_idx is None:
                print(f"DEBUG PREVIEW (No Header Found):\n{df_preview.to_string()}")
                header_row_idx = 0
                
            # Read actual data with the found header
            df = pd.read_excel(io.BytesIO(file_bytes), header=header_row_idx)
        except Exception as e:
            raise ValueError(f"Could not read Excel file: {e}")

        # Normalize column names for flexible matching
        df.columns = df.columns.astype(str).str.strip().str.lower()
        print(f"DEBUG: Parsed Excel columns: {df.columns.tolist()}")
        
        # Try to find common column names for Symbol, Quantity, Avg Price, Current Price
        symbol_col = next((c for c in df.columns if any(x in c for x in ['instrument', 'symbol', 'stock', 'company', 'name', 'asset', 'fund'])), None)
        qty_col = next((c for c in df.columns if any(x in c for x in ['qty', 'quantity', 'shares', 'balance', 'available', 'units'])), None)
        avg_price_col = next((c for c in df.columns if any(x in c for x in ['avg', 'cost', 'invested price', 'buy price', 'purchase'])), None)
        curr_price_col = next((c for c in df.columns if any(x in c for x in ['cmp', 'ltp', 'market price', 'nav', 'current price', 'close'])), None)
        invested_col = next((c for c in df.columns if any(x in c for x in ['invested', 'investment', 'amount', 'buy value'])), None)
        current_value_col = next((c for c in df.columns if any(x in c for x in ['current value', 'market value', 'present value', 'closing value'])), None)
        pnl_col = next((c for c in df.columns if any(x in c for x in ['unrealised', 'unrealized', 'p&l', 'pnl', 'profit', 'loss'])), None)

        if not symbol_col or not qty_col:
            raise ValueError(f"Excel file missing required columns. Found columns: {df.columns.tolist()}. Could not identify Symbol and Quantity columns.")

        def _clean_num(val):
            if pd.isna(val): return 0.0
            try:
                s = str(val).replace('₹', '').replace('Rs', '').replace(',', '').strip()
                return float(s)
            except:
                return 0.0

        # Delete ALL previous holdings across all sources to clear portfolio data
        await self.repo.delete_all_holdings()

        # Pre-fetch metadata for all unique symbols to ensure we have the correct Name and Sector
        unique_symbols = set()
        for _, row in df.iterrows():
            symbol = str(row[symbol_col]).strip().upper()
            if symbol and symbol != 'NAN':
                unique_symbols.add(symbol)
                
        import asyncio
        from services.market_data.fetchers import YFinanceFetcher
        fetcher = YFinanceFetcher()
        async def fetch_meta(sym):
            return await asyncio.to_thread(fetcher.fetch_fundamentals, sym)
            
        meta_tasks = [fetch_meta(sym) for sym in unique_symbols]
        meta_results = await asyncio.gather(*meta_tasks, return_exceptions=True)
        meta_map = dict(zip(unique_symbols, meta_results))

        upserted_count = 0
        for _, row in df.iterrows():
            symbol = str(row[symbol_col]).strip().upper()
            if not symbol or symbol == 'NAN':
                continue
                
            qty = _clean_num(row[qty_col])
            if qty <= 0:
                continue
                
            avg_price = _clean_num(row[avg_price_col]) if avg_price_col else 0.0
            curr_price = _clean_num(row[curr_price_col]) if curr_price_col else avg_price
            
            invested_val = _clean_num(row[invested_col]) if invested_col else (qty * avg_price)
            curr_val = _clean_num(row[current_value_col]) if current_value_col else (qty * curr_price)
            
            if pnl_col:
                pnl = _clean_num(row[pnl_col])
            else:
                pnl = curr_val - invested_val
                
            pnl_pct = (pnl / invested_val * 100) if invested_val > 0 else 0.0

            # Find or create stock with fetched metadata
            info = meta_map.get(symbol, {})
            if isinstance(info, Exception):
                info = {}
            name = info.get("longName") or symbol
            sector = info.get("sector")

            stock = await self.market_repo.get_stock_by_symbol(symbol)
            if not stock:
                # We need to upsert it manually since get_stock_by_symbol might return None for inactive stocks
                from sqlalchemy import text
                res = await self.db.execute(
                    text("""
                        INSERT INTO stocks (symbol, name, sector, is_active) 
                        VALUES (:symbol, :name, :sector, true) 
                        ON CONFLICT (symbol) DO UPDATE SET 
                            is_active = true, 
                            name = EXCLUDED.name, 
                            sector = COALESCE(EXCLUDED.sector, stocks.sector)
                        RETURNING id
                    """),
                    {"symbol": symbol, "name": name, "sector": sector}
                )
                stock_id = res.scalar()
            else:
                stock_id = stock["id"]
                # Optionally, update existing stock if metadata is newly found
                if sector and not stock.get("sector"):
                    from sqlalchemy import text
                    await self.db.execute(
                        text("UPDATE stocks SET sector = :sector, name = :name WHERE id = :id"),
                        {"sector": sector, "name": name, "id": stock_id}
                    )

            # Try to fetch latest live price from DB if current price wasn't specified in the excel file or matches avg_price
            if not curr_price_col or curr_price <= 0 or curr_price == avg_price:
                stock_data = await self.market_repo.get_ohlcv_daily(stock_id, limit=1)
                if stock_data and len(stock_data) > 0 and stock_data[0].get("close"):
                    curr_price = float(stock_data[0]["close"])
                    curr_val = qty * curr_price
                    if not pnl_col:
                        pnl = curr_val - invested_val
                    pnl_pct = (pnl / invested_val * 100) if invested_val > 0 else 0.0

            holding = {
                "stock_id": str(stock_id),
                "quantity": qty,
                "avg_buy_price": avg_price,
                "current_price": curr_price,
                "invested_value": invested_val,
                "current_value": curr_val,
                "pnl": pnl,
                "pnl_pct": pnl_pct,
                "source": source
            }
            await self.repo.upsert_holding(holding)
            upserted_count += 1

        await self.db.commit()
        return {"success": True, "holdings_imported": upserted_count}

    async def get_summary(self, source: str = "paper") -> dict:
        """Get portfolio summary statistics."""
        await self.sync_live_prices(source)
        holdings = await self.repo.get_holdings(source)

        total_value = float(sum(h.get("current_value") or 0 for h in holdings))
        invested_value = float(sum(h.get("invested_value") or 0 for h in holdings))
        total_pnl = total_value - invested_value
        total_pnl_pct = (total_pnl / invested_value * 100) if invested_value > 0 else 0
        daily_pnl = float(sum(h.get("day_change") or 0 for h in holdings))
        daily_pnl_pct = (daily_pnl / total_value * 100) if total_value > 0 else 0

        return {
            "total_value": round(total_value, 2),
            "invested_value": round(invested_value, 2),
            "total_pnl": round(total_pnl, 2),
            "total_pnl_pct": round(total_pnl_pct, 2),
            "daily_pnl": round(daily_pnl, 2),
            "daily_pnl_pct": round(daily_pnl_pct, 2),
            "num_holdings": len(holdings),
        }

    async def get_health(self, source: str = "paper") -> dict:
        """Calculate portfolio health scores."""
        await self.sync_live_prices(source)
        holdings = await self.repo.get_holdings(source)

        if not holdings:
            return {
                "health_score": 0,
                "diversification_score": 0,
                "concentration_risk": 100,
                "sector_allocation": {},
                "top_holdings": [],
                "recommendations": ["No holdings found. Start building your portfolio."],
            }

        total_value = float(sum(h.get("current_value") or 0 for h in holdings))

        # Sector allocation
        sector_values: dict[str, float] = {}
        for h in holdings:
            sector = h.get("sector") or "Unknown"
            sector_values[sector] = sector_values.get(sector, 0) + float(h.get("current_value") or 0)

        sector_allocation = {
            s: round(v / total_value * 100, 2) if total_value > 0 else 0
            for s, v in sector_values.items()
        }

        # Concentration risk (HHI)
        weights = [float(h.get("current_value") or 0) / total_value for h in holdings] if total_value > 0 else []
        hhi = sum(w**2 for w in weights) * 10000  # scale to 0-10000
        concentration_risk = min(100, hhi / 100)

        # Diversification score
        n_sectors = len([s for s in sector_values.keys() if s != "Unknown"])
        if n_sectors > 1 and total_value > 0:
            sector_weights = [v / total_value for k, v in sector_values.items() if k != "Unknown"]
            entropy = -sum(w * math.log(w) for w in sector_weights if w > 0)
            max_entropy = math.log(n_sectors)
            diversification_score = (entropy / max_entropy * 100) if max_entropy > 0 else 0
        else:
            # Fallback to stock-level diversification if sectors are unknown
            n_stocks = len(holdings)
            if n_stocks > 1 and total_value > 0:
                stock_weights = [(float(h.get("current_value") or 0)) / total_value for h in holdings]
                entropy = -sum(w * math.log(w) for w in stock_weights if w > 0)
                max_entropy = math.log(n_stocks)
                diversification_score = (entropy / max_entropy * 100) if max_entropy > 0 else 0
            else:
                diversification_score = 0

        # Health score (composite)
        pnl_trend_score = 50  # neutral default
        if holdings:
            positive_holdings = sum(1 for h in holdings if (h.get("pnl") or 0) > 0)
            pnl_trend_score = (positive_holdings / len(holdings)) * 100

        health_score = (
            pnl_trend_score * 0.30 +
            diversification_score * 0.25 +
            (100 - concentration_risk) * 0.25 +
            min(len(holdings) / 10 * 100, 100) * 0.20  # more holdings = better (up to 10)
        )

        # Top holdings
        sorted_holdings = sorted(holdings, key=lambda h: h.get("current_value") or 0, reverse=True)
        top_holdings = [
            {"symbol": h["symbol"], "name": h["name"], "weight_pct": round(
                ((h.get("current_value") or 0) / total_value * 100) if total_value > 0 else 0, 2
            )}
            for h in sorted_holdings[:5]
        ]

        # Recommendations
        recommendations = []
        if concentration_risk > 50:
            recommendations.append("High concentration risk — consider diversifying across more stocks.")
        if n_sectors < 3:
            recommendations.append("Low sector diversification — consider adding stocks from different sectors.")
        max_weight = max(weights) * 100 if weights else 0
        if max_weight > 25:
            recommendations.append(f"Single stock exceeds 25% of portfolio — consider rebalancing.")
        if not recommendations:
            recommendations.append("Portfolio is well-diversified. Keep monitoring for opportunities.")

        return {
            "health_score": round(health_score, 1),
            "diversification_score": round(diversification_score, 1),
            "concentration_risk": round(concentration_risk, 1),
            "sector_allocation": sector_allocation,
            "top_holdings": top_holdings,
            "recommendations": recommendations,
        }

    async def get_equity_curve(self, source: str = "paper", days: int = 30) -> list[dict]:
        """Generate synthetic historical equity curve based on current holdings."""
        holdings = await self.get_holdings(source)
        if not holdings:
            return []

        from services.market_data.fetchers import YFinanceFetcher
        fetcher = YFinanceFetcher()
        
        # Determine period string for yfinance
        period = "1mo"
        if days > 30:
            period = "3mo"
        if days > 90:
            period = "6mo"
        if days > 180:
            period = "1y"

        # Fetch historical data for all holdings
        historical_data = {}
        for h in holdings:
            symbol = h["symbol"]
            qty = h.get("quantity", 0)
            if qty <= 0:
                continue
                
            df = fetcher.fetch_ohlcv(symbol, period=period, interval="1d", is_index=False)
            if not df.empty and 'timestamp' in df.columns:
                # Keep only timestamp and close price
                # We need to normalize dates to ignore time components
                df['date_str'] = pd.to_datetime(df['timestamp']).dt.strftime('%Y-%m-%d')
                df['value'] = df['close'] * qty
                
                # Create a dict of date -> value
                historical_data[symbol] = dict(zip(df['date_str'], df['value']))

        if not historical_data:
            return []

        # Aggregate across all dates
        all_dates = set()
        for sym_data in historical_data.values():
            all_dates.update(sym_data.keys())
            
        sorted_dates = sorted(list(all_dates))
        
        # Truncate to the requested number of days
        if len(sorted_dates) > days:
            sorted_dates = sorted_dates[-days:]

        curve = []
        for d in sorted_dates:
            daily_total = 0.0
            for symbol in historical_data:
                # If a stock doesn't have data for this day (e.g. holiday for that specific stock?), 
                # we try to get the exact day, or we just skip. 
                # For a synthetic curve, getting the exact day value is fine.
                val = historical_data[symbol].get(d, 0.0)
                daily_total += val
                
            if daily_total > 0:
                curve.append({
                    "date": d,
                    "value": round(daily_total, 2)
                })

        # Forward fill zeros if necessary (e.g. missing data on a day)
        # For simplicity, if daily_total is > 0 we keep it. If a day is 0, we might want to skip or fill.
        # Our loop above naturally skips completely 0 days if all stocks are missing,
        # but if only some are missing, it might dip. A robust way is to ffill in pandas, 
        # but for this synthetic curve, the basic dict sum works well enough.
        
        return curve
