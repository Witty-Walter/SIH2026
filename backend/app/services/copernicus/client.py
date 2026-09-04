import copernicusmarine
import xarray as xr
import pandas as pd
from datetime import datetime, timezone
from config import settings

import random

_dataset_cache = {}

def get_dataset(dataset_id: str):
    """Returns a cached xarray dataset connection."""
    pass

def get_sst(min_lat: float, max_lat: float, min_lon: float, max_lon: float, time_str: str = None) -> dict:
    """
    Returns mocked SST data for a specific bounding box to prevent OOM on free tier.
    """
    dataset_id = "cmems_mod_glo_phy_anfc_0.083deg_PT1H-m"
    
    selected_time = time_str if time_str else datetime.now(timezone.utc).isoformat()
    return {
        "value": float(round(28.5 + random.uniform(-1.5, 1.5), 2)),
        "unit": "degrees_C",
        "data_timestamp": selected_time,
        "dataset_id": dataset_id
    }

def get_chlorophyll(min_lat: float, max_lat: float, min_lon: float, max_lon: float, time_str: str = None) -> dict:
    """
    Returns mocked Chlorophyll-a data for a specific bounding box to prevent OOM on free tier.
    """
    dataset_id = "cmems_mod_glo_bgc-pft_anfc_0.25deg_P1D-m"
    
    selected_time = time_str if time_str else datetime.now(timezone.utc).isoformat()
    return {
        "value": float(round(0.4 + random.uniform(-0.2, 0.3), 3)),
        "unit": "mg/m3",
        "data_timestamp": selected_time,
        "dataset_id": dataset_id
    }
