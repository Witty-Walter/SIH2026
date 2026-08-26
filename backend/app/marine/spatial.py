from typing import Tuple, Dict

def resolve_area_to_bbox(area_id: str) -> Tuple[float, float, float, float]:
    """
    Resolves an area_id to a bounding box (min_lat, max_lat, min_lon, max_lon).
    In a real app, this would query PostGIS (NeonDB) for the polygon geometry and call ST_Extent().
    For the MVP test, we mock a few known areas.
    """
    mock_areas: Dict[str, Tuple[float, float, float, float]] = {
        "AREA_001": (20.5, 21.0, 70.1, 70.8), # Veraval Deep Fishing Zone
        "AREA_002": (18.8, 19.3, 72.0, 72.5), # Mumbai West Fishing Zone
        "AREA_003": (11.5, 12.2, 73.0, 73.8), # Lakshadweep Channel Zone
    }
    
    if area_id in mock_areas:
        return mock_areas[area_id]
    
    # Fallback default
    return (15.0, 15.5, 74.0, 74.5)
