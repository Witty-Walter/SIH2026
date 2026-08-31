-- Enable PostGIS extension
CREATE EXTENSION IF NOT EXISTS postgis;

-- ============================================================
-- Fishing areas (predefined, named zones)
-- ============================================================
CREATE TABLE IF NOT EXISTS fishing_areas (
    id          SERIAL PRIMARY KEY,
    area_code   VARCHAR(20) UNIQUE NOT NULL,  -- e.g. 'AREA_001'
    name        VARCHAR(100) NOT NULL,          -- e.g. 'Veraval Deep Sea Zone'
    description TEXT,
    geom        GEOMETRY(Polygon, 4326) NOT NULL,
    created_at  TIMESTAMPTZ DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_fishing_areas_geom ON fishing_areas USING GIST(geom);

-- ============================================================
-- PFZ data (updated daily, from INCOIS pre-download)
-- ============================================================
CREATE TABLE IF NOT EXISTS pfz_zones (
    id              SERIAL PRIMARY KEY,
    source          VARCHAR(50),                  -- 'INCOIS', 'MODEL'
    valid_date      DATE NOT NULL,
    probability     VARCHAR(10) NOT NULL,          -- 'HIGH', 'MEDIUM', 'LOW'
    sst_celsius     FLOAT,
    chlorophyll_mgm3 FLOAT,
    geom            GEOMETRY(Geometry, 4326) NOT NULL,
    created_at      TIMESTAMPTZ DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_pfz_geom ON pfz_zones USING GIST(geom);
CREATE INDEX IF NOT EXISTS idx_pfz_date ON pfz_zones(valid_date);

-- ============================================================
-- Restricted/sensitive zones (static — geofencing)
-- ============================================================
CREATE TABLE IF NOT EXISTS restricted_zones (
    id          SERIAL PRIMARY KEY,
    name        VARCHAR(100) NOT NULL,
    zone_type   VARCHAR(50) NOT NULL,   -- 'NAVY_TEST', 'MPA', 'EEZ_BOUNDARY', 'ECOLOGICALLY_SENSITIVE'
    severity    INT NOT NULL DEFAULT 1,  -- 1=warning, 2=hard block
    geom        GEOMETRY(Geometry, 4326) NOT NULL,  -- Can be Polygon or LineString
    notes       TEXT
);
CREATE INDEX IF NOT EXISTS idx_restricted_geom ON restricted_zones USING GIST(geom);

-- ============================================================
-- Active alerts (cyclone, tsunami, high wave warnings)
-- ============================================================
CREATE TABLE IF NOT EXISTS alerts (
    id          SERIAL PRIMARY KEY,
    alert_type  VARCHAR(50) NOT NULL,   -- 'CYCLONE', 'HIGH_WAVE', 'LIGHTNING', 'TSUNAMI'
    severity    INT NOT NULL,           -- 1=advisory, 2=warning, 3=emergency
    title       VARCHAR(200),
    description TEXT,
    valid_from  TIMESTAMPTZ,
    valid_until TIMESTAMPTZ,
    source      VARCHAR(50),            -- 'IMD', 'INCOIS', 'NDMA'
    geom        GEOMETRY(Polygon, 4326),
    is_active   BOOLEAN DEFAULT TRUE
);
CREATE INDEX IF NOT EXISTS idx_alerts_geom ON alerts USING GIST(geom);

-- ============================================================
-- Conversation sessions (multi-turn memory backup)
-- ============================================================
CREATE TABLE IF NOT EXISTS conversations (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id         VARCHAR(100),
    started_at      TIMESTAMPTZ DEFAULT NOW(),
    last_active     TIMESTAMPTZ DEFAULT NOW(),
    state_snapshot  JSONB    -- Serialized AgentState for context persistence
);
