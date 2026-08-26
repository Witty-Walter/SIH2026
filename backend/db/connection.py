import asyncpg
import ssl
from typing import Optional
from config import settings

class Database:
    def __init__(self):
        self.pool: Optional[asyncpg.Pool] = None

    async def connect(self):
        if not self.pool:
            raw_url = settings.database_url.replace("postgresql+asyncpg://", "postgresql://")
            # Neon requires sslmode=require. asyncpg needs ssl context or string explicitly.
            # If the URL contains sslmode=require, we need to pass ssl='require' explicitly.
            use_ssl = "sslmode=require" in raw_url or "neon.tech" in raw_url
            
            self.pool = await asyncpg.create_pool(
                dsn=raw_url,
                ssl='require' if use_ssl else None,
                min_size=1,
                max_size=5
            )

    async def disconnect(self):
        if self.pool:
            await self.pool.close()
            self.pool = None

    async def fetch(self, query: str, *args):
        if not self.pool:
            await self.connect()
        async with self.pool.acquire() as connection:
            return await connection.fetch(query, *args)

    async def fetchrow(self, query: str, *args):
        if not self.pool:
            await self.connect()
        async with self.pool.acquire() as connection:
            return await connection.fetchrow(query, *args)

    async def execute(self, query: str, *args):
        if not self.pool:
            await self.connect()
        async with self.pool.acquire() as connection:
            return await connection.execute(query, *args)

db = Database()
