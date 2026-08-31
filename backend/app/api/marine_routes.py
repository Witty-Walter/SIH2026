from fastapi import APIRouter, HTTPException, Query
from datetime import datetime, timezone
from cachetools import cached, TTLCache
from typing import List
from app.marine.models import MarineObservation
from app.marine.spatial import resolve_area_to_bbox
from app.services.copernicus.client import get_sst, get_chlorophyll
from app.services.weather.client import get_weather
import asyncio

router = APIRouter(prefix="/marine-data", tags=["Marine"])

# Simple in-memory cache: Cache up to 100 requests for 1 hour (3600 seconds)
# This prevents duplicate requests to Copernicus for the same area within an hour.
cache = TTLCache(maxsize=100, ttl=3600)

@router.get("", response_model=List[MarineObservation])
async def get_marine_data(
    area_id: str = Query(..., description="The ID of the fishing area or polygon"),
    start_time: str = Query(None, description="ISO timestamp for observation or forecast"),
    variables: str = Query("sst", description="Comma separated list of variables to fetch")
):
    try:
        # 1. Resolve area_id to geographic bounding box
        min_lat, max_lat, min_lon, max_lon = resolve_area_to_bbox(area_id)
        
        # 2. Call Copernicus and Weather services concurrently
        # For weather, we use the centroid of the bounding box
        centroid_lat = (min_lat + max_lat) / 2.0
        centroid_lon = (min_lon + max_lon) / 2.0
        
        # Run synchronous Copernicus in a thread, and async weather
        copernicus_sst_task = asyncio.to_thread(
            get_sst, min_lat, max_lat, min_lon, max_lon, start_time
        )
        copernicus_chl_task = asyncio.to_thread(
            get_chlorophyll, min_lat, max_lat, min_lon, max_lon, start_time
        )
        weather_task = get_weather(centroid_lat, centroid_lon, start_time)
        
        copernicus_data, chl_data, weather_data_list = await asyncio.gather(
            copernicus_sst_task, copernicus_chl_task, weather_task
        )
        
        # 3. Determine if this was an observation (past) or forecast (future)
        req_time = datetime.fromisoformat(start_time.replace('Z', '+00:00')) if start_time else datetime.now(timezone.utc)
        obs_type = "forecast" if req_time > datetime.now(timezone.utc) else "observation"
        
        # 4. Normalize to standardized schema
        observations = []
        
        # Add SST
        observations.append(
            MarineObservation(
                area_id=area_id,
                latitude=centroid_lat,
                longitude=centroid_lon,
                timestamp=start_time or datetime.now(timezone.utc).isoformat(),
                variable="sst_c",
                value=copernicus_data["value"],
                unit=copernicus_data["unit"],
                source="Copernicus Marine",
                dataset_id=copernicus_data["dataset_id"],
                observation_or_forecast=obs_type,
                data_timestamp=copernicus_data["data_timestamp"],
                retrieval_timestamp=datetime.now(timezone.utc).isoformat()
            )
        )
        
        # Add Chlorophyll
        observations.append(
            MarineObservation(
                area_id=area_id,
                latitude=centroid_lat,
                longitude=centroid_lon,
                timestamp=start_time or datetime.now(timezone.utc).isoformat(),
                variable="chlorophyll_mgm3",
                value=chl_data["value"],
                unit=chl_data["unit"],
                source="Copernicus Marine",
                dataset_id=chl_data["dataset_id"],
                observation_or_forecast=obs_type,
                data_timestamp=chl_data["data_timestamp"],
                retrieval_timestamp=datetime.now(timezone.utc).isoformat()
            )
        )
        
        # Add Weather variables
        for w in weather_data_list:
            observations.append(
                MarineObservation(
                    area_id=area_id,
                    latitude=centroid_lat,
                    longitude=centroid_lon,
                    timestamp=start_time or datetime.now(timezone.utc).isoformat(),
                    variable=w["variable"],
                    value=w["value"],
                    unit=w["unit"],
                    source="Open-Meteo",
                    dataset_id=w["dataset_id"],
                    observation_or_forecast=obs_type,
                    data_timestamp=w["data_timestamp"],
                    retrieval_timestamp=datetime.now(timezone.utc).isoformat()
                )
            )
        
        return observations
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
