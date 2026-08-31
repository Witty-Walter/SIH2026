import asyncio
from db.connection import db

async def run():
    await db.connect()
    rows = await db.fetch('SELECT source, probability, sst_celsius, chlorophyll_mgm3 FROM pfz_zones LIMIT 3')
    print([dict(r) for r in rows])
    await db.disconnect()

asyncio.run(run())
