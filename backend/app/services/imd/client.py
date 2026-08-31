"""
IMD / NDMA CAP (Common Alerting Protocol) service.

Fetches live cyclone and severe-weather alerts from the NDMA Sachet CAP feed,
converts them to PostGIS-compatible records, and inserts them into the `alerts` table.

The fetch is intentionally designed to be called from a background task / startup hook
so it can run on a schedule without blocking any API route.
"""

import httpx
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from db.connection import db

# Namespace used in CAP 1.2 XML
CAP_NS = {"cap": "urn:oasis:names:tc:emergency:cap:1.2"}

# Primary NDMA Sachet feed
RSS_FEED_URL = "https://sachet.ndma.gov.in/cap_public_website/rss/rss_india.xml"

# Keywords that indicate a marine/cyclone hazard
MARINE_KEYWORDS = [
    "cyclone", "depression", "storm", "squall", "high wave",
    "rough sea", "strong wind", "tsunami", "tidal",
]

SEVERITY_MAP = {
    "Extreme": 3,
    "Severe":  3,
    "Moderate": 2,
    "Minor":   1,
    "Unknown": 1,
}


def _text(element, tag: str, ns: dict = CAP_NS) -> str | None:
    """Safe helper to extract text from a CAP element."""
    node = element.find(tag, ns)
    return node.text.strip() if node is not None and node.text else None


def _cap_polygon_to_wkt(cap_polygon: str) -> str | None:
    """
    Convert a CAP polygon string like "lat1,lon1 lat2,lon2 ..." to WKT.
    Note: CAP uses lat,lon order; WKT (and PostGIS) uses lon lat order.
    """
    try:
        pairs = cap_polygon.strip().split()
        coords = []
        for pair in pairs:
            parts = pair.split(",")
            lat, lon = float(parts[0]), float(parts[1])
            coords.append(f"{lon} {lat}")
        # Close the ring
        if coords and coords[0] != coords[-1]:
            coords.append(coords[0])
        return f"POLYGON(({', '.join(coords)}))"
    except Exception:
        return None


def _cap_circle_to_wkt(cap_circle: str) -> str | None:
    """
    Convert a CAP circle like "lat,lon radius" to a rough rectangular WKT.
    radius is in km; we approximate ~0.009 degrees per km.
    """
    try:
        parts = cap_circle.strip().split()
        latlon = parts[0].split(",")
        lat, lon = float(latlon[0]), float(latlon[1])
        radius_km = float(parts[1])
        deg = radius_km * 0.009
        return (
            f"POLYGON(({lon - deg} {lat - deg}, {lon + deg} {lat - deg}, "
            f"{lon + deg} {lat + deg}, {lon - deg} {lat + deg}, {lon - deg} {lat - deg}))"
        )
    except Exception:
        return None


async def fetch_and_store_imd_alerts() -> int:
    """
    Fetch IMD/NDMA CAP alerts via their RSS feed, filter for marine-relevant events, and
    upsert them into the `alerts` PostGIS table.
    """
    inserted = 0
    cap_links = []

    # 1. Fetch the RSS Feed to get the active alert links
    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            resp = await client.get(RSS_FEED_URL)
            resp.raise_for_status()
            rss_root = ET.fromstring(resp.content)
            # Find all <item><link> elements
            for item in rss_root.findall(".//item"):
                link = item.find("link")
                if link is not None and link.text:
                    cap_links.append(link.text.strip())
    except Exception as e:
        print(f"[IMD] Could not fetch RSS feed: {e}")

    if not cap_links:
        print("[IMD] No active alerts found in RSS feed or feed failed. Using fallback mock alert for demo.")
        await _insert_demo_alert()
        return 1

    # 2. Fetch each individual CAP XML
    async with httpx.AsyncClient(timeout=15.0) as client:
        for cap_url in cap_links:
            try:
                cap_resp = await client.get(cap_url)
                cap_resp.raise_for_status()
                root = ET.fromstring(cap_resp.content)
            except Exception as e:
                print(f"[IMD] Failed to fetch or parse CAP XML from {cap_url}: {e}")
                continue

            # CAP feeds can be a single <alert> or an <alerts> wrapper
            alerts_elements = root.findall(".//cap:alert", CAP_NS)
            if not alerts_elements:
                # Try root itself if it IS an alert
                if root.tag.endswith("alert"):
                    alerts_elements = [root]

            for alert_el in alerts_elements:
                for info_el in alert_el.findall("cap:info", CAP_NS):
                    event = _text(info_el, "cap:event") or ""
                    headline = _text(info_el, "cap:headline") or event
                    severity_str = _text(info_el, "cap:severity") or "Unknown"
                    valid_from_str = _text(info_el, "cap:onset") or _text(info_el, "cap:sent")
                    valid_until_str = _text(info_el, "cap:expires")
                    description = _text(info_el, "cap:description")
                    alert_type = "CYCLONE"

                    # Filter only marine-relevant alerts
                    if not any(kw in event.lower() or kw in headline.lower() for kw in MARINE_KEYWORDS):
                        continue

                    # Parse geography
                    wkt = None
                    area_el = info_el.find("cap:area", CAP_NS)
                    if area_el is not None:
                        polygon_el = area_el.find("cap:polygon", CAP_NS)
                        circle_el = area_el.find("cap:circle", CAP_NS)
                        if polygon_el is not None and polygon_el.text:
                            wkt = _cap_polygon_to_wkt(polygon_el.text)
                        elif circle_el is not None and circle_el.text:
                            wkt = _cap_circle_to_wkt(circle_el.text)

                    if not wkt:
                        continue  # Can't store without geometry

                    severity = SEVERITY_MAP.get(severity_str, 1)

                    # Parse timestamps
                    try:
                        valid_from = datetime.fromisoformat(valid_from_str) if valid_from_str else None
                    except ValueError:
                        valid_from = None

                    try:
                        valid_until = datetime.fromisoformat(valid_until_str) if valid_until_str else None
                    except ValueError:
                        valid_until = None

                    # Upsert into DB (title is unique enough for dedup)
                    await db.execute(
                        """
                        INSERT INTO alerts
                            (alert_type, severity, title, description, valid_from, valid_until, source, geom, is_active)
                        VALUES
                            ($1, $2, $3, $4, $5, $6, 'IMD', ST_MakeValid(ST_GeomFromText($7, 4326)), TRUE)
                        ON CONFLICT DO NOTHING
                        """,
                        alert_type,
                        severity,
                        headline,
                        description,
                        valid_from,
                        valid_until,
                        wkt,
                    )
                    inserted += 1

    print(f"[IMD] Inserted {inserted} new marine alerts from live feed.")
    return inserted


async def _insert_demo_alert():
    """Insert a mock cyclone alert in the Bay of Bengal for demo purposes."""
    # 300km offshore Chennai
    demo_wkt = (
        "POLYGON(("
        "81.0 11.0, 82.5 11.0, 82.5 12.5, 81.0 12.5, 81.0 11.0"
        "))"
    )
    await db.execute(
        """
        INSERT INTO alerts
            (alert_type, severity, title, description, valid_from, valid_until, source, geom, is_active)
        VALUES
            ($1, $2, $3, $4, $5, $6, 'IMD_DEMO', ST_GeomFromText($7, 4326), TRUE)
        ON CONFLICT DO NOTHING
        """,
        "CYCLONE",
        3,
        "DEMO: Deep Depression BOB 2026 — Bay of Bengal",
        "A deep depression has formed in the Bay of Bengal approximately 300km east of Chennai. "
        "Rough seas and strong winds expected. Fishermen are advised NOT to venture into sea.",
        datetime.now(timezone.utc),
        None,
        demo_wkt,
    )
    print("[IMD] Demo cyclone alert inserted.")
