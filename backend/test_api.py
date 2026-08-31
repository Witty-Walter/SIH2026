import asyncio
from app.api.marine_routes import resolve_area_to_bbox
from app.services.copernicus.client import get_sst, get_chlorophyll

async def main():
    area_id = "AREA_001"
    try:
        min_lat, max_lat, min_lon, max_lon = 10, 15, 70, 75
        time_str = "2026-08-31T16:00:00Z"
        print(f"Testing get_sst with {time_str}...")
        sst = get_sst(min_lat, max_lat, min_lon, max_lon, time_str)
        print(sst)
        
        print(f"Testing get_chlorophyll with {time_str}...")
        chl = get_chlorophyll(min_lat, max_lat, min_lon, max_lon, time_str)
        print(chl)
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(main())
