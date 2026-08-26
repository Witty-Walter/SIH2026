import httpx
from datetime import datetime, timezone
from typing import List

async def get_weather(lat: float, lon: float, time_str: str = None) -> List[dict]:
    """
    Fetches wind and precipitation data from Open-Meteo for a specific coordinate.
    """
    # Open-Meteo Marine/Weather API
    url = "https://api.open-meteo.com/v1/forecast"
    
    params = {
        "latitude": lat,
        "longitude": lon,
        "current": "wind_speed_10m,wind_direction_10m,precipitation",
        "hourly": "wind_speed_10m,wind_direction_10m,precipitation",
        "wind_speed_unit": "kmh",
        "precipitation_unit": "mm",
        "timezone": "auto"
    }
    
    try:
        async with httpx.AsyncClient() as client:
            r = await client.get(url, params=params, timeout=10.0)
            r.raise_for_status()
            data = r.json()
            
            # Extract current data
            current = data.get("current", {})
            
            # We return a list of dictionaries that will be normalized into MarineObservations
            # in the router.
            selected_time = datetime.now(timezone.utc).isoformat()
            
            return [
                {
                    "variable": "wind_speed",
                    "value": current.get("wind_speed_10m", 0.0),
                    "unit": "kmh",
                    "data_timestamp": selected_time,
                    "dataset_id": "open-meteo-forecast"
                },
                {
                    "variable": "wind_direction",
                    "value": current.get("wind_direction_10m", 0.0),
                    "unit": "degrees",
                    "data_timestamp": selected_time,
                    "dataset_id": "open-meteo-forecast"
                },
                {
                    "variable": "precipitation",
                    "value": current.get("precipitation", 0.0),
                    "unit": "mm",
                    "data_timestamp": selected_time,
                    "dataset_id": "open-meteo-forecast"
                }
            ]
            
    except Exception as e:
        print(f"Weather API error: {e}")
        return []
