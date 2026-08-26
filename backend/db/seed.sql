-- 5 realistic fishing areas near Indian coast
INSERT INTO fishing_areas (area_code, name, geom) VALUES
('AREA_001', 'Veraval Deep Fishing Zone',
  ST_GeomFromText('POLYGON((70.1 20.5, 70.8 20.5, 70.8 21.0, 70.1 21.0, 70.1 20.5))', 4326)),
('AREA_002', 'Mumbai West Fishing Zone',
  ST_GeomFromText('POLYGON((72.0 18.8, 72.5 18.8, 72.5 19.3, 72.0 19.3, 72.0 18.8))', 4326)),
('AREA_003', 'Lakshadweep Channel Zone',
  ST_GeomFromText('POLYGON((73.0 11.5, 73.8 11.5, 73.8 12.2, 73.0 12.2, 73.0 11.5))', 4326))
ON CONFLICT (area_code) DO NOTHING;

-- 2 restricted zones
INSERT INTO restricted_zones (name, zone_type, severity, geom) VALUES
('Mumbai Naval Exercise Area', 'NAVY_TEST', 2,
  ST_GeomFromText('POLYGON((72.6 18.9, 73.0 18.9, 73.0 19.3, 72.6 19.3, 72.6 18.9))', 4326)),
('Gulf of Kutch MPA', 'MPA', 1,
  ST_GeomFromText('POLYGON((69.0 22.3, 69.8 22.3, 69.8 22.8, 69.0 22.8, 69.0 22.3))', 4326));

-- Sample PFZ entries (would be refreshed daily in production)
INSERT INTO pfz_zones (source, valid_date, probability, sst_celsius, chlorophyll_mgm3, geom) VALUES
('INCOIS', CURRENT_DATE, 'HIGH', 27.8, 1.4,
  ST_GeomFromText('POLYGON((70.3 20.6, 70.6 20.6, 70.6 20.9, 70.3 20.9, 70.3 20.6))', 4326)),
('INCOIS', CURRENT_DATE, 'MEDIUM', 28.2, 0.9,
  ST_GeomFromText('POLYGON((72.1 19.0, 72.4 19.0, 72.4 19.2, 72.1 19.2, 72.1 19.0))', 4326));
