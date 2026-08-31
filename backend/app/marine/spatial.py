from typing import Tuple, Dict
from db.connection import db

async def resolve_area_to_bbox(area_id: str) -> Tuple[float, float, float, float]:
    """
    Resolves an area_id to a bounding box (min_lat, max_lat, min_lon, max_lon).
    First checks mock hardcoded zones, then queries PostGIS for real zones.
    """
    mock_areas: Dict[str, Tuple[float, float, float, float]] = {
        "AREA_001": (20.5, 21.0, 70.1, 70.8), # Veraval Deep Fishing Zone
        "AREA_002": (18.8, 19.3, 72.0, 72.5), # Mumbai West Fishing Zone
        "AREA_003": (11.5, 12.2, 73.0, 73.8), # Lakshadweep Channel Zone
    }
    
    if area_id in mock_areas:
        return mock_areas[area_id]
        
    # Query PostGIS
    try:
        record = await db.fetchrow(
            "SELECT ST_YMin(geom) as min_lat, ST_YMax(geom) as max_lat, "
            "ST_XMin(geom) as min_lon, ST_XMax(geom) as max_lon "
            "FROM fishing_areas WHERE area_code = $1", area_id
        )
        if record:
            return (record['min_lat'], record['max_lat'], record['min_lon'], record['max_lon'])
    except Exception as e:
        print(f"Error querying bbox for {area_id}: {e}")
    
    # Fallback default
    return (15.0, 15.5, 74.0, 74.5)
