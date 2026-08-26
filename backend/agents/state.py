from typing import TypedDict, Annotated, Optional, List
from langgraph.graph.message import add_messages

class Intent(TypedDict):
    action: str         # "check_safety" | "find_pfz" | "compare_zones" | "route" | "alert_check"
    entities: dict      # {"zone_name": "Area A", "time": "tomorrow_morning"}
    language: str       # "en" | "hi" | "ta" | "ml" | "bn" | ...

class LocationContext(TypedDict):
    user_lat: float
    user_lon: float
    target_zone_id: Optional[str]   # "AREA_001" — from DB
    target_polygon_wkt: Optional[str]  # WKT string from PostGIS
    target_bbox: Optional[dict]     # {min_lat, max_lat, min_lon, max_lon}

class OceanData(TypedDict):
    wave_height_m: float
    wave_period_s: float
    wind_speed_kmh: float
    wind_direction_deg: float
    sst_celsius: Optional[float]
    current_speed_ms: Optional[float]
    tide_height_m: Optional[float]
    data_time: str      # ISO timestamp of forecast

class GISData(TypedDict):
    in_restricted_zone: bool
    restricted_zone_name: Optional[str]
    distance_to_nearest_boundary_km: float
    intersecting_mpa: Optional[str]
    route_crosses_restricted: bool  # for simple straight-line route check

class PFZData(TypedDict):
    is_active_pfz: bool
    pfz_probability: str        # "HIGH" | "MEDIUM" | "LOW" | "NONE"
    chlorophyll_mgm3: Optional[float]
    sst_celsius: Optional[float]
    nearest_pfz_distance_km: Optional[float]
    nearest_pfz_id: Optional[str]

class RiskResult(TypedDict):
    status: str             # "SAFE" | "CAUTION" | "UNSAFE"
    safety_score: int       # 0-100, higher = safer
    fishing_score: int      # 0-100, higher = better fishing
    hard_blocks: List[str]  # Reasons for absolute block
    warnings: List[str]     # Soft warnings
    confidence: str         # "HIGH" | "MEDIUM" | "LOW" (data quality)

class AlternativeZone(TypedDict):
    zone_id: str
    zone_name: str
    distance_km: float
    risk: RiskResult
    pfz: PFZData

class AgentState(TypedDict):
    # Conversation
    messages: Annotated[list, add_messages]
    user_language: str          # Detected on first turn, persisted

    # Session context (persists across turns)
    current_location: Optional[LocationContext]
    selected_area_id: Optional[str]

    # Per-turn data (reset each turn)
    intent: Optional[Intent]
    ocean_data: Optional[OceanData]
    gis_data: Optional[GISData]
    pfz_data: Optional[PFZData]
    risk_result: Optional[RiskResult]
    alternative_zones: Optional[List[AlternativeZone]]

    # Output
    response_text: Optional[str]
    map_data: Optional[dict]     # GeoJSON FeatureCollection for frontend
    alerts: Optional[List[dict]] # [{type, severity, message}]
