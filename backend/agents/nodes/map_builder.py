from agents.state import AgentState
import json

async def map_builder_node(state: AgentState) -> dict:
    context = state.get("current_location", {})
    risk = state.get("risk_result", {})
    wkt = context.get("target_polygon_wkt")
    
    features = []
    
    # 1. Add User Location (if available)
    if "user_lat" in context and "user_lon" in context:
        features.append({
            "type": "Feature",
            "geometry": {
                "type": "Point",
                "coordinates": [context["user_lon"], context["user_lat"]] # GeoJSON uses [lon, lat]
            },
            "properties": {
                "label": "Your Location",
                "icon": "boat"
            }
        })
        
    # 2. Add Target Zone (if polygon exists)
    if wkt and wkt.startswith("POLYGON"):
        # Very hacky WKT to GeoJSON coordinate conversion for MVP
        # WKT: POLYGON((lon lat, lon lat, ...))
        coord_str = wkt.replace("POLYGON((", "").replace("))", "")
        pairs = coord_str.split(",")
        coords = []
        for pair in pairs:
            lon, lat = pair.strip().split()
            coords.append([float(lon), float(lat)])
            
        color = "#22c55e" # Green
        if risk.get("status") == "CAUTION": color = "#eab308" # Yellow
        elif risk.get("status") == "UNSAFE": color = "#ef4444" # Red
            
        features.append({
            "type": "Feature",
            "geometry": {
                "type": "Polygon",
                "coordinates": [coords]
            },
            "properties": {
                "id": context.get("target_zone_id", "unknown"),
                "label": "Target Area",
                "status": risk.get("status", "UNKNOWN"),
                "color": color,
                "fill_opacity": 0.3
            }
        })
        
    map_data = {
        "type": "FeatureCollection",
        "features": features
    }
    
    return {"map_data": map_data}
