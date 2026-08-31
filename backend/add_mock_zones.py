import asyncio
from db.connection import db

async def main():
    await db.connect()
    try:
        # Add Chennai Coastal Zone
        await db.execute("""
            INSERT INTO fishing_areas (area_code, name, geom) VALUES
            ('AREA_004', 'Chennai Coastal Zone',
              ST_GeomFromText('POLYGON((80.3 12.9, 80.5 12.9, 80.5 13.1, 80.3 13.1, 80.3 12.9))', 4326))
            ON CONFLICT (area_code) DO NOTHING;
        """)
        
        # Add Coromandel Deep
        await db.execute("""
            INSERT INTO fishing_areas (area_code, name, geom) VALUES
            ('AREA_005', 'Coromandel Deep',
              ST_GeomFromText('POLYGON((80.5 12.7, 80.8 12.7, 80.8 12.9, 80.5 12.9, 80.5 12.7))', 4326))
            ON CONFLICT (area_code) DO NOTHING;
        """)
        
        # Add High PFZ in Chennai Coastal Zone
        await db.execute("""
            INSERT INTO pfz_zones (source, valid_date, probability, sst_celsius, chlorophyll_mgm3, geom) VALUES
            ('INCOIS', CURRENT_DATE, 'HIGH', 28.5, 2.1,
              ST_GeomFromText('POLYGON((80.35 12.95, 80.45 12.95, 80.45 13.05, 80.35 13.05, 80.35 12.95))', 4326))
        """)
        
        print("Successfully inserted Chennai mock zones!")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        await db.disconnect()

asyncio.run(main())
