import asyncio
import httpx
import json
import os
import sys

# Add parent directory to path to import db
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from db.connection import db

OVERPASS_URL = "https://overpass-api.de/api/interpreter"
HEADERS = {"User-Agent": "MarineHackathon/1.0 (contact@example.com)"}

# Bounding boxes to chunk the queries so we don't time out
BBOXES = [
    {"name": "West_Coast", "bbox": "8.0,68.0,24.0,75.0"},
    {"name": "East_Coast", "bbox": "8.0,79.0,22.0,89.0"},
    {"name": "South_Coast", "bbox": "6.0,75.0,10.0,79.0"},
]

async def fetch_and_insert(client, bbox_name, bbox):
    print(f"Fetching data for {bbox_name}...")
    
    # Query for Harbours (Fishing areas)
    query_harbour = f"""
    [out:json][timeout:60];
    (
      way["harbour"="yes"]({bbox});
      relation["harbour"="yes"]({bbox});
    );
    out geom;
    """
    
    # Query for Nature Reserves (MPAs) and Naval/Danger areas
    query_restricted = f"""
    [out:json][timeout:60];
    (
      way["leisure"="nature_reserve"]({bbox});
      relation["leisure"="nature_reserve"]({bbox});
      way["military"="danger_area"]({bbox});
      relation["military"="danger_area"]({bbox});
      way["military"="naval_base"]({bbox});
      relation["military"="naval_base"]({bbox});
    );
    out geom;
    """
    
    # Fetch Harbours
    try:
        r = await client.post(OVERPASS_URL, data={'data': query_harbour}, headers=HEADERS, timeout=90.0)
        data = r.json()
        harbours_inserted = 0
        for element in data.get('elements', []):
            if 'geometry' in element:
                coords = [f"{pt['lon']} {pt['lat']}" for pt in element['geometry'] if 'lon' in pt and 'lat' in pt]
                if not coords or len(coords) < 3: continue
                if coords[0] != coords[-1]: coords.append(coords[0]) # Close ring
                wkt = f"POLYGON(({', '.join(coords)}))"
                osm_id = str(element['id'])
                name = element.get('tags', {}).get('name', f'OSM Harbour {osm_id}')
                
                await db.execute("""
                    INSERT INTO fishing_areas (area_code, name, geom) 
                    VALUES ($1, $2, ST_MakeValid(ST_GeomFromText($3, 4326)))
                    ON CONFLICT (area_code) DO NOTHING
                """, f"OSM_{osm_id}", name, wkt)
                harbours_inserted += 1
        print(f"  Inserted {harbours_inserted} harbours for {bbox_name}")
    except Exception as e:
        print(f"  Error fetching harbours for {bbox_name}: {e}")
        if 'r' in locals(): print(r.text[:200])

    # Fetch Restricted Zones
    try:
        r = await client.post(OVERPASS_URL, data={'data': query_restricted}, headers=HEADERS, timeout=90.0)
        data = r.json()
        restricted_inserted = 0
        for element in data.get('elements', []):
            if 'geometry' in element:
                tags = element.get('tags', {})
                zone_type = "MPA" if tags.get("leisure") == "nature_reserve" else "NAVY_TEST"
                severity = 1 if zone_type == "MPA" else 2
                
                coords = [f"{pt['lon']} {pt['lat']}" for pt in element['geometry'] if 'lon' in pt and 'lat' in pt]
                if not coords or len(coords) < 3: continue
                if coords[0] != coords[-1]: coords.append(coords[0])
                wkt = f"POLYGON(({', '.join(coords)}))"
                osm_id = str(element['id'])
                name = tags.get('name', f'OSM Restricted {osm_id}')
                
                await db.execute("""
                    INSERT INTO restricted_zones (name, zone_type, severity, geom)
                    VALUES ($1, $2, $3, ST_MakeValid(ST_GeomFromText($4, 4326)))
                """, name, zone_type, severity, wkt)
                restricted_inserted += 1
        print(f"  Inserted {restricted_inserted} restricted zones for {bbox_name}")
    except Exception as e:
        print(f"  Error fetching restricted zones for {bbox_name}: {e}")

async def main():
    await db.connect()
    
    # 1. Alter table to support generic Geometry type (so ST_MakeValid can insert multipolygons if needed)
    try:
        await db.execute("ALTER TABLE fishing_areas ALTER COLUMN geom TYPE GEOMETRY(Geometry, 4326)")
        print("Updated fishing_areas geom type to GEOMETRY.")
    except Exception as e:
        print(f"Note: {e}")
        
    async with httpx.AsyncClient() as client:
        for b in BBOXES:
            await fetch_and_insert(client, b["name"], b["bbox"])
            await asyncio.sleep(2) # be nice to Overpass
            
    await db.disconnect()

if __name__ == "__main__":
    asyncio.run(main())
