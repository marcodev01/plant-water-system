#!/usr/bin/env python3

from typing import Optional

from pydantic import BaseModel

class PlantConfiguration(BaseModel):
    id: Optional[str] = None # id required but generated on severside
    sensor_type: str
    mac_adress: Optional[str] = None
    sensor_channel: Optional[int] = None
    plant: str
    relay_pin: int
    water_duration_sec: int = 2
    water_iterations: int = 1
    max_moisture: int
    min_moisture: int
    max_conductivity: Optional[int] = None
    min_conductivity: Optional[int] = None
