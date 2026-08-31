from agents.state import AgentState
from db.connection import db
import asyncio
from app.services.incois.dynamic import compute_dynamic_pfzs

async def context_node(state: AgentState) -> dict:
    intent = state.get("intent", {})
    entities = intent.get("entities", {})
    zone_name = entities.get("zone_name")
    
    current_location = state.get("current_location", {})
    
    # If LLM didn't find a zone name, try to use the previously selected one from session state
    if not zone_name and state.get("selected_area_id"):
        # We need to fetch it by ID instead
        record = await db.fetchrow(
            "SELECT area_code, ST_AsText(geom) as wkt, ST_XMin(geom) as min_lon, ST_XMax(geom) as max_lon, ST_YMin(geom) as min_lat, ST_YMax(geom) as max_lat FROM fishing_areas WHERE area_code = $1", 
            state["selected_area_id"]
        )
        if record:
            current_location["target_zone_id"] = record["area_code"]
            current_location["target_polygon_wkt"] = record["wkt"]
            current_location["target_bbox"] = {
                "min_lon": record["min_lon"], "max_lon": record["max_lon"],
                "min_lat": record["min_lat"], "max_lat": record["max_lat"]
            }
            return {"current_location": current_location}
            
    if zone_name:
        # Search DB by name (case insensitive, partial match)
        query = """
            SELECT area_code, ST_AsText(geom) as wkt, 
                   ST_XMin(geom) as min_lon, ST_XMax(geom) as max_lon, 
                   ST_YMin(geom) as min_lat, ST_YMax(geom) as max_lat
            FROM fishing_areas 
            WHERE name ILIKE $1 
            LIMIT 1
        """
        record = await db.fetchrow(query, f"%{zone_name}%")
        if record:
            current_location["target_zone_id"] = record["area_code"]
            current_location["target_polygon_wkt"] = record["wkt"]
            current_location["target_bbox"] = {
                "min_lon": record["min_lon"], "max_lon": record["max_lon"],
                "min_lat": record["min_lat"], "max_lat": record["max_lat"]
            }
            return {
                "current_location": current_location,
                "selected_area_id": record["area_code"] # Persist for next turns
            }
    
    # If no zone found or specified, default to user's point coordinates if available
    if not current_location.get("target_polygon_wkt") and "user_lat" in current_location:
        lat = current_location["user_lat"]
        lon = current_location["user_lon"]
        # Create a large bbox around the user (100km radius) so it reaches the ocean
        current_location["target_bbox"] = {
            "min_lat": lat - 1.0, "max_lat": lat + 1.0,
            "min_lon": lon - 1.0, "max_lon": lon + 1.0
        }
        # Point WKT
        current_location["target_polygon_wkt"] = f"POINT({lon} {lat})"
        
    # Execute Dynamic PFZ engine if we have a bbox
    dynamic_pfzs = []
    if current_location.get("target_bbox"):
        loop = asyncio.get_event_loop()
        dynamic_pfzs = await loop.run_in_executor(
            None, 
            compute_dynamic_pfzs, 
            current_location["target_bbox"]
        )
        
    return {
        "current_location": current_location,
        "dynamic_pfzs": dynamic_pfzs
    }
