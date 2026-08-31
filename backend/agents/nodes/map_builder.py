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
        # WKT: POLYGON((lon lat, lon lat, ...))
        # Handle optional space after POLYGON
        coord_str = wkt.replace("POLYGON", "").replace("(", "").replace(")", "")
        pairs = coord_str.split(",")
        coords = []
        for pair in pairs:
            parts = pair.strip().split()
            if len(parts) >= 2:
                coords.append([float(parts[0]), float(parts[1])])
            
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
        
    # 3. Add Alternative Zones
    alternative_zones = state.get("alternative_zones", [])
    
    # Sort alternative zones to find the best one
    sorted_alts = sorted(
        alternative_zones, 
        key=lambda x: (x.get("risk", {}).get("fishing_score", 0), x.get("risk", {}).get("safety_score", 0)), 
        reverse=True
    )
    
    for i, alt in enumerate(sorted_alts):
        alt_wkt = alt.get("wkt")
        is_best = (i == 0) and len(sorted_alts) > 0
        
        if alt_wkt and alt_wkt.startswith("POLYGON"):
            coord_str = alt_wkt.replace("POLYGON", "").replace("(", "").replace(")", "")
            pairs = coord_str.split(",")
            alt_coords = []
            for pair in pairs:
                parts = pair.strip().split()
                if len(parts) >= 2:
                    alt_coords.append([float(parts[0]), float(parts[1])])
                    
            label = alt.get('zone_name')
            if is_best:
                label = f"⭐ RECOMMENDED: {label}"
            else:
                label = f"Alternative: {label}"
                
            features.append({
                "type": "Feature",
                "geometry": {
                    "type": "Polygon",
                    "coordinates": [alt_coords]
                },
                "properties": {
                    "id": alt.get("zone_id", "unknown"),
                    "label": f"{label} (Fishing: {alt.get('risk', {}).get('fishing_score', 0)})",
                    "status": alt.get("risk", {}).get("status", "UNKNOWN"),
                    "color": "#10b981" if is_best else "#3b82f6", # Emerald for best, Blue for others
                    "fill_opacity": 0.4 if is_best else 0.2
                }
            })
            
    # 4. Add Dynamic On-Demand PFZ Polygons
    dynamic_pfzs = state.get("dynamic_pfzs", [])
    if dynamic_pfzs:
        # These are already fully formatted GeoJSON Feature dicts
        for feat in dynamic_pfzs:
            # Set specific colors based on probability
            prob = feat["properties"].get("status", "LOW")
            if prob == "HIGH":
                feat["properties"]["color"] = "#10b981" # Emerald
                feat["properties"]["fill_opacity"] = 0.45
            elif prob == "MEDIUM":
                feat["properties"]["color"] = "#f59e0b" # Amber
                feat["properties"]["fill_opacity"] = 0.25
            features.append(feat)
            
    map_data = {
        "type": "FeatureCollection",
        "features": features
    }
    
    return {"map_data": map_data}
