import httpx
from agents.state import AgentState
from datetime import datetime, timedelta, timezone

async def ocean_node(state: AgentState) -> dict:
    intent = state.get("intent", {})
    entities = intent.get("entities", {})
    
    # Extract time
    time_str = entities.get("time", "now")
    target_date = datetime.now(timezone.utc)
    if time_str and "tomorrow" in time_str.lower():
        target_date += timedelta(days=1)
        target_date = target_date.replace(hour=6, minute=0, second=0)
        
    iso_time = target_date.strftime("%Y-%m-%dT%H:00:00Z")
    
    # Extract area. The context node resolves the target_zone_id.
    # For this MVP test, we fallback to our mocked AREA_001
    context = state.get("current_location", {})
    area_id = context.get("target_zone_id") or "AREA_001"
    
    try:
        async with httpx.AsyncClient() as client:
            # Call our own normalized Copernicus endpoint
            r = await client.get(
                "http://127.0.0.1:8000/marine-data",
                params={"area_id": area_id, "start_time": iso_time},
                timeout=60.0
            )
            r.raise_for_status()
            ocean_data = r.json()
            
        return {"ocean_data": ocean_data}
    except Exception as e:
        print(f"Failed to fetch Copernicus data: {e}")
        return {"ocean_data": {"error": "Copernicus service unavailable"}}
