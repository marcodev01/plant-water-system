#!/usr/bin/env python3

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel


class Plant(BaseModel):
    id: str
    name: str
    moisture: int
    conductivity: Optional[int] = None
    sunlight: Optional[int] = None
    temperature: Optional[float] = None
    batteryLevel: Optional[int] = None


class PlantSensorEntry(BaseModel):
    ts: str
    plants: List[Plant]
    temperature: float
    humidity: float
    visible_light: int
    UV_index: float
    IR_light: int

