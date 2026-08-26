from typing import Dict, Any

def calculate_risk(ocean: Dict[str, Any], gis: Dict[str, Any], pfz: Dict[str, Any]) -> Dict[str, Any]:
    hard_blocks = []
    warnings = []

    # --- HARD BLOCKS (instant UNSAFE) ---
    if gis.get("cyclone_alert"):
        hard_blocks.append("Active cyclone warning in this region")
    if gis.get("in_restricted_zone"):
        hard_blocks.append(f"Zone is inside restricted area: {gis.get('restricted_zone_name', 'Unknown')}")
    if ocean.get("wave_height", 0) > 3.5:
        hard_blocks.append(f"Extremely high waves: {ocean.get('wave_height')}m — life-threatening")

    if hard_blocks:
        return {
            "status": "UNSAFE", "safety_score": 0, "fishing_score": 0,
            "hard_blocks": hard_blocks, "warnings": [], "confidence": "HIGH"
        }

    # --- SOFT SCORING (0-100, higher = safer) ---
    safety_score = 100
    wave_height = ocean.get("wave_height", 0)
    wind_speed = ocean.get("wind_speed", 0)
    
    if wave_height > 2.5:
        safety_score -= 40
        warnings.append(f"High waves: {wave_height}m (threshold: 2.5m)")
    elif wave_height > 1.5:
        safety_score -= 15
        warnings.append(f"Moderate waves: {wave_height}m")

    if wind_speed > 40:
        safety_score -= 30
        warnings.append(f"Strong winds: {wind_speed} km/h")
    elif wind_speed > 25:
        safety_score -= 10
        warnings.append(f"Moderate winds: {wind_speed} km/h")

    if gis.get("distance_to_nearest_boundary_km", 999) < 10:
        safety_score -= 20
        warnings.append(f"Close to maritime boundary: {gis.get('distance_to_nearest_boundary_km'):.1f}km")

    # --- FISHING SCORE (0-100) ---
    pfz_map = {"HIGH": 90, "MEDIUM": 60, "LOW": 30, "NONE": 10}
    fishing_score = pfz_map.get(pfz.get("pfz_probability", "NONE"), 10)

    status = "SAFE" if safety_score >= 60 else "CAUTION" if safety_score >= 30 else "UNSAFE"

    return {
        "status": status, "safety_score": max(0, safety_score), "fishing_score": fishing_score,
        "hard_blocks": [], "warnings": warnings, "confidence": "HIGH"
    }
