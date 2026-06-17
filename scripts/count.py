import asyncio
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from sqlalchemy import text
from apps.api.database import async_session_factory

async def main():
    async with async_session_factory() as session:
        res = await session.execute(text("SELECT count(*) FROM ohlcv_daily"))
        print("Rows in ohlcv_daily:", res.scalar())
        res = await session.execute(text("SELECT count(*) FROM signals"))
        print("Rows in signals:", res.scalar())

if __name__ == "__main__":
    asyncio.run(main())
