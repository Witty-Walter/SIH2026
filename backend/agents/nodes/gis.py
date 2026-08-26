from agents.state import AgentState
from db.connection import db

async def gis_node(state: AgentState) -> dict:
    context = state.get("current_location", {})
    wkt = context.get("target_polygon_wkt")
    
    gis_data = {
        "in_restricted_zone": False,
        "restricted_zone_name": None,
        "distance_to_nearest_boundary_km": 999.0,
        "route_crosses_restricted": False
    }
    
    if wkt:
        # Check intersection with restricted zones
        query = """
            SELECT name, zone_type 
            FROM restricted_zones 
            WHERE ST_Intersects(geom, ST_GeomFromText($1, 4326))
            LIMIT 1
        """
        record = await db.fetchrow(query, wkt)
        if record:
            gis_data["in_restricted_zone"] = True
            gis_data["restricted_zone_name"] = record["name"]
            
        # Optional: check distance to nearest boundary
        # If user location is known and target is a polygon, check if route intersects
        if "user_lat" in context:
            user_pt = f"POINT({context['user_lon']} {context['user_lat']})"
            route_query = """
                SELECT name 
                FROM restricted_zones 
                WHERE ST_Intersects(geom, ST_MakeLine(ST_GeomFromText($1, 4326), ST_Centroid(ST_GeomFromText($2, 4326))))
                LIMIT 1
            """
            route_rec = await db.fetchrow(route_query, user_pt, wkt)
            if route_rec:
                gis_data["route_crosses_restricted"] = True
                
        # Mocking active cyclone alerts in GIS node (this could come from IMD in a real scenario)
        gis_data["cyclone_alert"] = False 

    return {"gis_data": gis_data}
