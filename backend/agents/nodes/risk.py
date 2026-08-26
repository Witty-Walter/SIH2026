from agents.state import AgentState
from tools.risk_engine import calculate_risk

async def risk_node(state: AgentState) -> dict:
    ocean_data_raw = state.get("ocean_data", [])
    
    # Flatten the list of MarineObservations into a dictionary for the risk engine
    ocean_dict = {}
    if isinstance(ocean_data_raw, list):
        for obs in ocean_data_raw:
            ocean_dict[obs.get("variable")] = obs.get("value")
    elif isinstance(ocean_data_raw, dict):
        ocean_dict = ocean_data_raw
        
    gis_data = state.get("gis_data", {})
    pfz_data = state.get("pfz_data", {})
    
    risk_result = calculate_risk(ocean_dict, gis_data, pfz_data)
    
    # In a full version, we'd also loop through alternative zones here if `user_wants_alternatives` is true
    alternative_zones = []
    
    return {
        "risk_result": risk_result,
        "alternative_zones": alternative_zones
    }
