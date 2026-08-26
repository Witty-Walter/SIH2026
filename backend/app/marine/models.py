from pydantic import BaseModel
from typing import Optional

class MarineObservation(BaseModel):
    area_id: str
    latitude: float
    longitude: float
    timestamp: str 
    variable: str
    value: float
    unit: str
    source: str
    dataset_id: str
    observation_or_forecast: str
    data_timestamp: str
    retrieval_timestamp: str
