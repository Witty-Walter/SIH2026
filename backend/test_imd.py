import asyncio
from app.services.imd.client import fetch_and_store_imd_alerts
from db.connection import db

async def test():
    await db.connect()
    await fetch_and_store_imd_alerts()
    await db.disconnect()

asyncio.run(test())
