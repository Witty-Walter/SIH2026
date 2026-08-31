import asyncio
from db.connection import db

async def run():
    await db.connect()
    await db.execute('ALTER TABLE pfz_zones ALTER COLUMN geom TYPE GEOMETRY(Geometry, 4326);')
    print("Altered pfz_zones geom column")
    await db.disconnect()

asyncio.run(run())
