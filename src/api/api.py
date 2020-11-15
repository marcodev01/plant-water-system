#!/usr/bin/env python3
from typing import Optional

from fastapi import FastAPI
from src.model.plant_configuration import PlantConfiguration
from src.model.app_type import AppType

import logging

# log configurations
logging.basicConfig(filename='../log/api.log',
                    filemode='a', 
                    format='%(asctime)s - %(levelname)s - %(message)s',
                    datefmt='%d-%m-%y %H:%M:%S', 
                    level=logging.INFO)
logger = logging.getLogger('api')

app = FastAPI()


@app.get("/app/status")
def api_status(app_type: Optional[AppType] = None):
    if app_type == AppType.api:
        return {"app": app_type, "status": "plant water api server is up!"}
    if app_type == AppType.water_app:
        return {"app": app_type ,"status": "plant water system is running!"}
    if app_type == None:
        return {"app": "here should be both states"}


@app.get("/app/log")
def get_app_log_fragment(app_type: AppType = AppType.api):
    pass

@app.get("/water-system/job/state") 
def change_plant_water_system_running_status(state: bool):
    pass

@app.get("/water-system/job/state")
def get_plant_water_job_status(): # read state
    pass


@app.get("/plants/configurations")
def get_all_plants_configurations():
    pass

@app.put("/plants/configurations/{plant_id}")
def change_plant_configuration(plant_id: int, plant_conf: PlantConfiguration):
    pass

@app.post("/plants/configurations")
def add_plant_configuration(plant_conf: PlantConfiguration):
    pass

@app.delete("/plants/configurations/{plant_id}")
def delete_plant_configuration(plant_id: int):
    pass

@app.get("/plants/history")
def get_plant_history(): # for specific range
    pass




