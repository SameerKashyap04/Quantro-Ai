import asyncio
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import logging

logging.basicConfig(level=logging.INFO, stream=sys.stdout)

from apps.api.tasks import scheduler_instance

async def main():
    print("Triggering EOD Pipeline Manually...")
    await scheduler_instance.run_eod_pipeline()
    print("Done!")

if __name__ == "__main__":
    asyncio.run(main())
