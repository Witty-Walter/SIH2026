import copernicusmarine
from datetime import datetime, timezone
import pandas as pd
from config import settings

def get_sst(min_lat: float, max_lat: float, min_lon: float, max_lon: float, time_str: str = None) -> dict:
    """
    Returns SST data for a specific bounding box using the Copernicus subset API to save memory.
    """
    dataset_id = "cmems_mod_glo_phy_anfc_0.083deg_PT1H-m"
    target_time = time_str if time_str else datetime.now(timezone.utc).isoformat()
    
    try:
        df = copernicusmarine.read_dataframe(
            dataset_id=dataset_id,
            variables=["thetao"],
            minimum_longitude=min_lon,
            maximum_longitude=max_lon,
            minimum_latitude=min_lat,
            maximum_latitude=max_lat,
            minimum_depth=0,
            maximum_depth=1,
            start_datetime=target_time,
            end_datetime=target_time,
            username=settings.copernicus_username,
            password=settings.copernicus_password,
            disable_progress_bar=True
        )
        
        mean_sst = df["thetao"].mean()
        
        return {
            "value": float(mean_sst),
            "unit": "degrees_C",
            "data_timestamp": target_time,
            "dataset_id": dataset_id
        }
    except Exception as e:
        print(f"Copernicus API error: {e}")
        raise e

def get_chlorophyll(min_lat: float, max_lat: float, min_lon: float, max_lon: float, time_str: str = None) -> dict:
    """
    Returns Chlorophyll-a data for a specific bounding box using the Copernicus subset API to save memory.
    """
    dataset_id = "cmems_mod_glo_bgc-pft_anfc_0.25deg_P1D-m"
    target_time = time_str if time_str else datetime.now(timezone.utc).isoformat()
    
    try:
        df = copernicusmarine.read_dataframe(
            dataset_id=dataset_id,
            variables=["chl"],
            minimum_longitude=min_lon,
            maximum_longitude=max_lon,
            minimum_latitude=min_lat,
            maximum_latitude=max_lat,
            minimum_depth=0,
            maximum_depth=1,
            start_datetime=target_time,
            end_datetime=target_time,
            username=settings.copernicus_username,
            password=settings.copernicus_password,
            disable_progress_bar=True
        )
        
        mean_chl = df["chl"].mean()
        
        return {
            "value": float(mean_chl),
            "unit": "mg/m3",
            "data_timestamp": target_time,
            "dataset_id": dataset_id
        }
    except Exception as e:
        print(f"Copernicus BGC API error: {e}")
        raise e
