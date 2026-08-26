from agents.state import AgentState
from db.connection import db

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
        # Create a small bbox around the user
        current_location["target_bbox"] = {
            "min_lat": lat - 0.1, "max_lat": lat + 0.1,
            "min_lon": lon - 0.1, "max_lon": lon + 0.1
        }
        # Point WKT
        current_location["target_polygon_wkt"] = f"POINT({lon} {lat})"
        
    return {"current_location": current_location}
