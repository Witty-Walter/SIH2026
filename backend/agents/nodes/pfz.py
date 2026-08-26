from agents.state import AgentState
from db.connection import db

async def pfz_node(state: AgentState) -> dict:
    context = state.get("current_location", {})
    wkt = context.get("target_polygon_wkt")
    
    pfz_data = {
        "is_active_pfz": False,
        "pfz_probability": "NONE"
    }
    
    if wkt:
        # Check if the target area IS a PFZ or overlaps heavily
        query = """
            SELECT probability
            FROM pfz_zones
            WHERE ST_Intersects(geom, ST_GeomFromText($1, 4326))
            ORDER BY 
              CASE probability WHEN 'HIGH' THEN 3 WHEN 'MEDIUM' THEN 2 WHEN 'LOW' THEN 1 ELSE 0 END DESC
            LIMIT 1
        """
        record = await db.fetchrow(query, wkt)
        if record:
            pfz_data["is_active_pfz"] = True
            pfz_data["pfz_probability"] = record["probability"]
            
    return {"pfz_data": pfz_data}
