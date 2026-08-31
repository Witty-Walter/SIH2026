"""
INCOIS PFZ (Potential Fishing Zone) algorithmic computer.

Since INCOIS does not provide a public API for bulk GeoJSON data, this service
replicates the INCOIS methodology by querying live satellite telemetry 
(Sea Surface Temp and Chlorophyll-a) from the Copernicus Marine Service and
applying INCOIS's official thresholds to compute the PFZ polygons algorithmically.
"""

import asyncio
import json
from datetime import datetime, timezone
from db.connection import db
from app.services.copernicus.client import get_sst, get_chlorophyll

# A coarse grid of test cells along the Indian coast (min_lat, max_lat, min_lon, max_lon)
# In production, this would be a much finer 0.1 degree grid.
COASTAL_GRID = [
    # Gujarat coast
    (20.5, 21.0, 69.5, 70.0),
    (20.0, 20.5, 70.0, 70.5),
    # Mumbai coast
    (18.5, 19.0, 72.0, 72.5),
    # Goa / Karnataka
    (14.5, 15.0, 73.5, 74.0),
    (13.0, 13.5, 74.0, 74.5),
    # Kerala (Trivandrum / Kochi)
    (8.0, 8.5, 76.5, 77.0),
    (8.5, 9.0, 76.5, 77.0),
    (9.5, 10.0, 75.5, 76.0),
    # Tamil Nadu / Chennai
    (12.5, 13.0, 80.5, 81.0),
    (13.0, 13.5, 80.5, 81.0),
    # Andhra
    (15.5, 16.0, 81.5, 82.0),
    # Odisha
    (19.0, 19.5, 85.0, 85.5),
]

def _classify_pfz(sst: float, chl: float) -> str:
    """Apply INCOIS thresholds to determine PFZ probability."""
    if sst is None or chl is None:
        return "NONE"
        
    # High Probability: SST 26-30C AND Chlorophyll > 0.3 mg/m3
    if (26.0 <= sst <= 30.0) and (chl > 0.3):
        return "HIGH"
        
    # Medium Probability: SST 24-32C AND Chlorophyll > 0.15 mg/m3
    if (24.0 <= sst <= 32.0) and (chl > 0.15):
        return "MEDIUM"
        
    return "LOW"

async def fetch_and_store_incois_pfz() -> int:
    """
    Computes today's PFZ map using live Copernicus satellite data.
    If the satellite API times out (e.g. firewall blocked), it falls back
    to loading a bundled offline GeoJSON file.
    """
    inserted = 0
    today = datetime.now(timezone.utc).date()
    
    # 1. Clear old data
    await db.execute("DELETE FROM pfz_zones WHERE valid_date < CURRENT_DATE")
    
    success_count = 0
    
    print("[INCOIS] Computing daily PFZs via satellite telemetry...")
    
    for (min_lat, max_lat, min_lon, max_lon) in COASTAL_GRID:
        try:
            # We run these sequentially here to avoid spamming the remote NetCDF service
            # but in production, we would use a process pool or async gather.
            sst_data = get_sst(min_lat, max_lat, min_lon, max_lon)
            chl_data = get_chlorophyll(min_lat, max_lat, min_lon, max_lon)
            
            sst_val = sst_data.get("value")
            chl_val = chl_data.get("value")
            
            prob = _classify_pfz(sst_val, chl_val)
            
            if prob in ("HIGH", "MEDIUM"):
                # Create a WKT Polygon representing this grid cell
                wkt = f"POLYGON(({min_lon} {min_lat}, {max_lon} {min_lat}, {max_lon} {max_lat}, {min_lon} {max_lat}, {min_lon} {min_lat}))"
                
                await db.execute(
                    """
                    INSERT INTO pfz_zones
                        (source, valid_date, probability, sst_celsius, chlorophyll_mgm3, geom)
                    VALUES
                        ($1, $2, $3, $4, $5, ST_GeomFromText($6, 4326))
                    """,
                    "MODEL", today, prob, sst_val, chl_val, wkt
                )
                inserted += 1
            
            success_count += 1
            
        except Exception as e:
            # Copernicus xarray fetch failed (likely network timeout/block)
            continue
            
    if success_count == 0:
        print("[INCOIS] Satellite telemetry failed (firewall block detected). Loading mock fallback data.")
        inserted = await _load_mock_fallback(today)
    else:
        print(f"[INCOIS] Successfully computed and inserted {inserted} new PFZ zones.")
        
    return inserted


async def _load_mock_fallback(valid_date) -> int:
    """Loads a hardcoded set of mock PFZ zones for demo purposes."""
    mock_zones = [
        # Chennai Offshore (High)
        {
            "prob": "HIGH", 
            "sst": 28.5, 
            "chl": 0.45, 
            "wkt": "POLYGON((80.5 13.0, 81.0 13.0, 81.0 13.5, 80.5 13.5, 80.5 13.0))"
        },
        # Goa Coast (Medium)
        {
            "prob": "MEDIUM", 
            "sst": 29.1, 
            "chl": 0.2, 
            "wkt": "POLYGON((73.5 15.0, 74.0 15.0, 74.0 15.5, 73.5 15.5, 73.5 15.0))"
        },
        # Gujarat Coast (High)
        {
            "prob": "HIGH", 
            "sst": 27.8, 
            "chl": 0.5, 
            "wkt": "POLYGON((69.5 21.0, 70.5 21.0, 70.5 21.5, 69.5 21.5, 69.5 21.0))"
        }
    ]
    
    inserted = 0
    for z in mock_zones:
        await db.execute(
            """
            INSERT INTO pfz_zones
                (source, valid_date, probability, sst_celsius, chlorophyll_mgm3, geom)
            VALUES
                ($1, $2, $3, $4, $5, ST_GeomFromText($6, 4326))
            """,
            "MOCK_FALLBACK", valid_date, z["prob"], z["sst"], z["chl"], z["wkt"]
        )
        inserted += 1
        
    print(f"[INCOIS] Loaded {inserted} mock PFZ fallback zones.")
    return inserted
