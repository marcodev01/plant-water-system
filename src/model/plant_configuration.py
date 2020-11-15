#!/usr/bin/env python3

from typing import Optional

from pydantic import BaseModel

class PlantConfiguration(BaseModel):
    sensor_type: str
    mac_adress: Optional[str] = None
    plant: str
    relay_pin: int
    water_duration_sec: Optional[int] = 2
    water_iterations: Optional[int] = 1
    max_moisture: int
    min_moisture: int
    max_conductivity: Optional[int] = None
    min_conductivity: Optional[int] = None
