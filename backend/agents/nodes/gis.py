from agents.state import AgentState
from db.connection import db

async def gis_node(state: AgentState) -> dict:
    context = state.get("current_location", {})
    wkt = context.get("target_polygon_wkt")
    
    gis_data = {
        "in_restricted_zone": False,
        "restricted_zone_name": None,
        "distance_to_nearest_boundary_km": 999.0,
        "route_crosses_restricted": False,
        "cyclone_alert": False,
        "cyclone_alert_title": None,
        "cyclone_alert_severity": None,
    }
    
    if wkt:
        # 1. Check intersection with restricted zones
        record = await db.fetchrow(
            """
            SELECT name, zone_type 
            FROM restricted_zones 
            WHERE ST_Intersects(geom, ST_GeomFromText($1, 4326))
            LIMIT 1
            """,
            wkt
        )
        if record:
            gis_data["in_restricted_zone"] = True
            gis_data["restricted_zone_name"] = record["name"]
            
        # 2. Check if route from user to target crosses a restricted zone
        if "user_lat" in context:
            user_pt = f"POINT({context['user_lon']} {context['user_lat']})"
            route_rec = await db.fetchrow(
                """
                SELECT name 
                FROM restricted_zones 
                WHERE ST_Intersects(
                    geom,
                    ST_MakeLine(
                        ST_GeomFromText($1, 4326),
                        ST_Centroid(ST_GeomFromText($2, 4326))
                    )
                )
                LIMIT 1
                """,
                user_pt,
                wkt
            )
            if route_rec:
                gis_data["route_crosses_restricted"] = True

        # 3. ✅ Real IMD alert check — query live `alerts` PostGIS table
        alert_rec = await db.fetchrow(
            """
            SELECT title, severity, description
            FROM alerts
            WHERE is_active = TRUE
              AND alert_type = 'CYCLONE'
              AND ST_Intersects(geom, ST_GeomFromText($1, 4326))
            ORDER BY severity DESC
            LIMIT 1
            """,
            wkt
        )
        if alert_rec:
            gis_data["cyclone_alert"] = True
            gis_data["cyclone_alert_title"] = alert_rec["title"]
            gis_data["cyclone_alert_severity"] = alert_rec["severity"]

    return {"gis_data": gis_data}
