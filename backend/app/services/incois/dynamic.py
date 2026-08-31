import datetime
from datetime import timezone
import pandas as pd
from app.services.copernicus.client import get_dataset
from app.services.incois.client import _classify_pfz

def compute_dynamic_pfzs(bbox: dict) -> list:
    """
    Computes PFZs dynamically for a given bounding box by querying Copernicus xarray datasets.
    Returns a list of GeoJSON Features representing HIGH and MEDIUM probability zones.
    This function blocks, so it should be run in an executor.
    """
    min_lat = bbox["min_lat"]
    max_lat = bbox["max_lat"]
    min_lon = bbox["min_lon"]
    max_lon = bbox["max_lon"]
    
    # Dataset IDs
    sst_dataset_id = "cmems_mod_glo_phy_anfc_0.083deg_PT1H-m"
    chl_dataset_id = "cmems_mod_glo_bgc-pft_anfc_0.25deg_P1D-m"
    
    try:
        # Get datasets
        ds_sst = get_dataset(sst_dataset_id)
        ds_chl = get_dataset(chl_dataset_id)
        
        # Spatial subset
        sst_subset = ds_sst.sel(latitude=slice(min_lat, max_lat), longitude=slice(min_lon, max_lon))
        chl_subset = ds_chl.sel(latitude=slice(min_lat, max_lat), longitude=slice(min_lon, max_lon))
        
        # Temporal subset (nearest to now)
        target_time = datetime.datetime.now(timezone.utc).replace(tzinfo=None)
        sst_subset = sst_subset.sel(time=target_time, method="nearest")
        chl_subset = chl_subset.sel(time=target_time, method="nearest")
        
        if "depth" in sst_subset.dims:
            sst_subset = sst_subset.sel(depth=0, method="nearest")
        if "depth" in chl_subset.dims:
            chl_subset = chl_subset.sel(depth=0, method="nearest")
            
        # Materialize to memory (this is the only blocking network call if cached)
        sst_subset = sst_subset.compute()
        chl_subset = chl_subset.compute()
        
    except Exception as e:
        print(f"Failed to fetch dynamic satellite data: {e}")
        return []
        
    features = []
    
    # Iterate through the finer SST grid (0.083 deg)
    lats = sst_subset.latitude.values
    lons = sst_subset.longitude.values
    
    # We create a small polygon block for each coordinate (e.g., +/- 0.04 degrees)
    delta = 0.0415
    
    for lat in lats:
        for lon in lons:
            try:
                # Cast to native python floats for JSON serialization
                p_lat = float(lat)
                p_lon = float(lon)
                
                sst_val = float(sst_subset['thetao'].sel(latitude=lat, longitude=lon).item())
                # For CHL, we find the nearest since it has a coarser grid
                chl_val = float(chl_subset['chl'].sel(latitude=lat, longitude=lon, method="nearest").item())
                
                prob = _classify_pfz(sst_val, chl_val)
                
                if prob in ("HIGH", "MEDIUM"):
                    features.append({
                        "type": "Feature",
                        "geometry": {
                            "type": "Polygon",
                            "coordinates": [[
                                [p_lon - delta, p_lat - delta],
                                [p_lon + delta, p_lat - delta],
                                [p_lon + delta, p_lat + delta],
                                [p_lon - delta, p_lat + delta],
                                [p_lon - delta, p_lat - delta]
                            ]]
                        },
                        "properties": {
                            "label": f"PFZ: {prob} Probability",
                            "status": prob,
                            "sst_celsius": round(sst_val, 2),
                            "chlorophyll_mgm3": round(chl_val, 2)
                        }
                    })
            except Exception:
                continue
                
    return features
