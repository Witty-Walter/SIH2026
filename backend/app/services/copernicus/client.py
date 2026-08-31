import copernicusmarine
import xarray as xr
import pandas as pd
from datetime import datetime, timezone
from config import settings

_dataset_cache = {}

def get_sst(min_lat: float, max_lat: float, min_lon: float, max_lon: float, time_str: str = None) -> dict:
    """
    Returns SST data for a specific bounding box from Copernicus using xarray spatial/temporal subsetting.
    """
    dataset_id = "cmems_mod_glo_phy_anfc_0.083deg_PT1H-m"
    
    try:
        # Open virtual dataset - avoids downloading the entire ocean!
        if dataset_id not in _dataset_cache:
            _dataset_cache[dataset_id] = copernicusmarine.open_dataset(
                dataset_id=dataset_id,
                username=settings.copernicus_username,
                password=settings.copernicus_password
            )
        ds = _dataset_cache[dataset_id]
        
        # Spatial subset
        ds_subset = ds.sel(
            latitude=slice(min_lat, max_lat),
            longitude=slice(min_lon, max_lon)
        )
        
        # Temporal subset
        if time_str:
            # Convert to pandas Timestamp to avoid xarray string comparison errors
            target_time = pd.to_datetime(time_str).tz_localize(None)
        else:
            target_time = datetime.now(timezone.utc).replace(tzinfo=None)
            
        ds_subset = ds_subset.sel(time=target_time, method="nearest")
        
        # Surface level
        if "depth" in ds_subset.dims:
            ds_subset = ds_subset.sel(depth=0, method="nearest")
            
        # Calculate spatial average for the requested bounding box
        # Since it's a remote dataset, xarray uses lazy dask arrays. We must call .compute()
        mean_sst = ds_subset['thetao'].mean().compute().item()
        selected_time = str(ds_subset.time.values)
        
        return {
            "value": float(mean_sst),
            "unit": "degrees_C",
            "data_timestamp": selected_time,
            "dataset_id": dataset_id
        }
    except Exception as e:
        print(f"Copernicus API error: {e}")
        # In a production app, we would raise HTTP exceptions here.
        raise e

def get_chlorophyll(min_lat: float, max_lat: float, min_lon: float, max_lon: float, time_str: str = None) -> dict:
    """
    Returns Chlorophyll-a data for a specific bounding box from Copernicus using xarray spatial/temporal subsetting.
    """
    dataset_id = "cmems_mod_glo_bgc-pft_anfc_0.25deg_P1D-m"
    
    try:
        if dataset_id not in _dataset_cache:
            _dataset_cache[dataset_id] = copernicusmarine.open_dataset(
                dataset_id=dataset_id,
                username=settings.copernicus_username,
                password=settings.copernicus_password
            )
        ds = _dataset_cache[dataset_id]
        
        ds_subset = ds.sel(
            latitude=slice(min_lat, max_lat),
            longitude=slice(min_lon, max_lon)
        )
        
        if time_str:
            target_time = pd.to_datetime(time_str).tz_localize(None)
        else:
            target_time = datetime.now(timezone.utc).replace(tzinfo=None)
            
        ds_subset = ds_subset.sel(time=target_time, method="nearest")
        
        if "depth" in ds_subset.dims:
            ds_subset = ds_subset.sel(depth=0, method="nearest")
            
        mean_chl = ds_subset['chl'].mean().compute().item()
        selected_time = str(ds_subset.time.values)
        
        return {
            "value": float(mean_chl),
            "unit": "mg/m3",
            "data_timestamp": selected_time,
            "dataset_id": dataset_id
        }
    except Exception as e:
        print(f"Copernicus BGC API error: {e}")
        raise e
