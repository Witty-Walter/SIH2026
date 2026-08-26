import asyncio
import httpx
from datetime import datetime, timezone

async def test_marine_endpoint():
    print("Testing local /marine-data endpoint...")
    async with httpx.AsyncClient() as client:
        try:
            r = await client.get(
                "http://127.0.0.1:8000/marine-data",
                params={
                    "area_id": "AREA_001",
                    "start_time": datetime.now(timezone.utc).isoformat()
                },
                timeout=30.0
            )
            r.raise_for_status()
            data = r.json()
            print("Success! Received:")
            for obs in data:
                print(obs)
        except Exception as e:
            print(f"Test failed: {e}")

if __name__ == "__main__":
    asyncio.run(test_marine_endpoint())
