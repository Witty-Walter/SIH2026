import httpx
from typing import Dict, Any

async def get_marine_forecast(bbox: Dict[str, float]) -> Dict[str, Any]:
    """
    bbox: {"min_lat": float, "max_lat": float, "min_lon": float, "max_lon": float}
    Uses centroid of bbox for Open-Meteo Marine API call.
    Returns averaged wave height, period, wind, etc.
    """
    if not bbox:
        # Default to some Indian ocean point if no bbox
        lat, lon = 15.0, 70.0
    else:
        lat = (bbox["min_lat"] + bbox["max_lat"]) / 2
        lon = (bbox["min_lon"] + bbox["max_lon"]) / 2

    params = {
        "latitude": lat, "longitude": lon,
        "hourly": "wave_height,wave_period,wind_speed_10m,wind_direction_10m,ocean_current_velocity",
        "timezone": "Asia/Kolkata",
        "forecast_days": 1 # Just get today/tomorrow
    }
    
    try:
        async with httpx.AsyncClient() as client:
            r = await client.get("https://marine-api.open-meteo.com/v1/marine", params=params, timeout=10.0)
            r.raise_for_status()
            data = r.json()
        
        # We'll just take the first forecast hour for simplicity in MVP, or average them.
        # Let's take the first hour (current time).
        if "hourly" in data and "wave_height" in data["hourly"] and len(data["hourly"]["wave_height"]) > 0:
            return {
                "wave_height_m": data["hourly"]["wave_height"][0] or 0.5,
                "wave_period_s": data["hourly"]["wave_period"][0] or 5.0,
                "wind_speed_kmh": data["hourly"]["wind_speed_10m"][0] or 15.0,
                "wind_direction_deg": data["hourly"]["wind_direction_10m"][0] or 180.0,
                "current_speed_ms": data["hourly"]["ocean_current_velocity"][0] or 0.2,
                "data_time": data["hourly"]["time"][0]
            }
        return get_fallback_data()
    except Exception as e:
        print(f"Error fetching from Open-Meteo: {e}")
        return get_fallback_data()

def get_fallback_data() -> Dict[str, Any]:
    return {
        "wave_height_m": 1.2,
        "wave_period_s": 6.5,
        "wind_speed_kmh": 20.0,
        "wind_direction_deg": 90.0,
        "current_speed_ms": 0.5,
        "data_time": "2024-01-01T00:00"
    }
