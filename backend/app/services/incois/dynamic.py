import datetime
from datetime import timezone
import pandas as pd
import copernicusmarine
from config import settings
from app.services.incois.client import _classify_pfz

def compute_dynamic_pfzs(bbox: dict) -> list:
    """
    Computes PFZs dynamically for a given bounding box using Copernicus dataframes.
    Returns a list of GeoJSON Features representing HIGH and MEDIUM probability zones.
    """
    # Add a 0.25 degree buffer (approx 25km) to ensure we capture coarse satellite grid points 
    # even if the target bounding box is very small.
    min_lat = bbox["min_lat"] - 0.25
    max_lat = bbox["max_lat"] + 0.25
    min_lon = bbox["min_lon"] - 0.25
    max_lon = bbox["max_lon"] + 0.25
    
    sst_dataset_id = "cmems_mod_glo_phy_anfc_0.083deg_PT1H-m"
    chl_dataset_id = "cmems_mod_glo_bgc-pft_anfc_0.25deg_P1D-m"
    
    target_time = datetime.datetime.now(timezone.utc).isoformat()
    
    try:
        df_sst = copernicusmarine.read_dataframe(
            dataset_id=sst_dataset_id,
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
        
        df_chl = copernicusmarine.read_dataframe(
            dataset_id=chl_dataset_id,
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
        
        sst_grid = df_sst.groupby(['latitude', 'longitude'])['thetao'].mean().reset_index()
        chl_grid = df_chl.groupby(['latitude', 'longitude'])['chl'].mean().reset_index()
        
    except Exception as e:
        print(f"Failed to fetch dynamic satellite data: {e}")
        return []
        
    features = []
    delta = 0.0415
    
    for _, srow in sst_grid.iterrows():
        lat = srow['latitude']
        lon = srow['longitude']
        sst_val = srow['thetao']
        
        dist = ((chl_grid['latitude'] - lat)**2 + (chl_grid['longitude'] - lon)**2)
        if len(dist) == 0:
            continue
        nearest_idx = dist.idxmin()
        chl_val = chl_grid.loc[nearest_idx, 'chl']
        
        prob = _classify_pfz(float(sst_val), float(chl_val))
        
        if prob in ("HIGH", "MEDIUM"):
            p_lat = float(lat)
            p_lon = float(lon)
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
                    "sst_celsius": round(float(sst_val), 2),
                    "chlorophyll_mgm3": round(float(chl_val), 2)
                }
            })
            
    return features
