import asyncio
from apps.api.database import async_session_factory
from apps.api.portfolio.service import PortfolioService

async def main():
    async with async_session_factory() as db:
        svc = PortfolioService(db)
        summary = await svc.get_summary("groww")
        print("SUMMARY:", summary)
        health = await svc.get_health("groww")
        print("HEALTH:", health)

asyncio.run(main())
