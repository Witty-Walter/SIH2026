from agents.state import AgentState
from tools.risk_engine import calculate_risk

async def risk_node(state: AgentState) -> dict:
    ocean_data_raw = state.get("ocean_data", [])
    
    # Flatten the list of MarineObservations into a dictionary for the risk engine
    ocean_dict = {}
    if isinstance(ocean_data_raw, list):
        for obs in ocean_data_raw:
            ocean_dict[obs.get("variable")] = obs.get("value")
    elif isinstance(ocean_data_raw, dict):
        ocean_dict = ocean_data_raw
        
    gis_data = state.get("gis_data", {})
    pfz_data = state.get("pfz_data", {})
    
    risk_result = calculate_risk(ocean_dict, gis_data, pfz_data)
    
    alternative_zones = []
    intent = state.get("intent", {})
    user_wants_alternatives = intent.get("entities", {}).get("user_wants_alternatives", False)
    current_location = state.get("current_location", {})
    
    if user_wants_alternatives and "user_lat" in current_location and "user_lon" in current_location:
        from db.connection import db
        import httpx
        import asyncio
        from datetime import datetime, timedelta, timezone
        
        # Get target time for the fallback queries
        time_str = intent.get("entities", {}).get("time", "now")
        target_date = datetime.now(timezone.utc)
        if time_str and "tomorrow" in time_str.lower():
            target_date += timedelta(days=1)
            target_date = target_date.replace(hour=6, minute=0, second=0)
        iso_time = target_date.strftime("%Y-%m-%dT%H:00:00Z")
        
        # Query DB for up to 3 nearest fishing areas within 200km
        query = """
            SELECT area_code, name, ST_AsText(geom) as wkt,
                   ST_Distance(geom::geography, ST_SetSRID(ST_MakePoint($2, $1), 4326)::geography) / 1000.0 as distance_km
            FROM fishing_areas
            WHERE ST_Distance(geom::geography, ST_SetSRID(ST_MakePoint($2, $1), 4326)::geography) < 200000
            ORDER BY geom <-> ST_SetSRID(ST_MakePoint($2, $1), 4326)
            LIMIT 3
        """
        records = await db.fetch(query, current_location["user_lat"], current_location["user_lon"])
        
        async with httpx.AsyncClient() as client:
            for record in records:
                # Skip the one they are already assessing if applicable
                if record["area_code"] == current_location.get("target_zone_id"):
                    continue
                    
                area_code = record["area_code"]
                
                # Fetch Ocean Data
                try:
                    import os
                    port = os.environ.get("PORT", "8000")
                    r = await client.get(
                        f"http://127.0.0.1:{port}/marine-data",
                        params={"area_id": area_code, "start_time": iso_time},
                        timeout=60.0
                    )
                    r.raise_for_status()
                    alt_ocean_data_raw = r.json()
                    
                    alt_ocean_dict = {obs["variable"]: obs["value"] for obs in alt_ocean_data_raw} \
                        if isinstance(alt_ocean_data_raw, list) else alt_ocean_data_raw
                        
                except Exception as e:
                    print(f"Failed to fetch ocean data for alternative {area_code}: {e}")
                    alt_ocean_dict = {"error": "unavailable"}
                    
                # Check PFZ
                pfz_query = """
                    SELECT probability
                    FROM pfz_zones
                    WHERE ST_Intersects(geom, ST_GeomFromText($1, 4326))
                    ORDER BY 
                      CASE probability WHEN 'HIGH' THEN 3 WHEN 'MEDIUM' THEN 2 WHEN 'LOW' THEN 1 ELSE 0 END DESC
                    LIMIT 1
                """
                pfz_rec = await db.fetchrow(pfz_query, record["wkt"])
                alt_pfz_data = {
                    "is_active_pfz": bool(pfz_rec),
                    "pfz_probability": pfz_rec["probability"] if pfz_rec else "NONE"
                }
                
                # Calculate risk
                alt_risk = calculate_risk(alt_ocean_dict, {}, alt_pfz_data)
                
                alternative_zones.append({
                    "zone_id": area_code,
                    "zone_name": record["name"],
                    "wkt": record["wkt"],
                    "distance_km": round(record["distance_km"], 2),
                    "risk": alt_risk,
                    "pfz": alt_pfz_data
                })
    
    return {
        "risk_result": risk_result,
        "alternative_zones": alternative_zones
    }
