#!/usr/bin/env python3
from typing import Optional

from fastapi import FastAPI
from tinydb.queries import Query, where
from src.model.plant_configuration import PlantConfiguration
from src.model.app_type import AppType
from src.db.db_adapter import DbAdapter
from src.api.api_helper import get_water_system_log_fragment, get_api_log_fragment
from src.waterSystem.water_system_runner import get_state_of_water_system, resume_water_system, pause_water_system

import logging

# log configurations
logging.basicConfig(filename='../log/api.log',
                    filemode='a', 
                    format='%(asctime)s - %(levelname)s - %(message)s',
                    datefmt='%d-%m-%y %H:%M:%S', 
                    level=logging.INFO)
logger = logging.getLogger('api')

# history db initialisation
plant_db = DbAdapter().plant_db
sensor_history = plant_db.table('sensor_history')
# master data db initialisation
master_data_db = DbAdapter().master_data_db
plants_configuration = master_data_db.table('plants_configuration')

app = FastAPI()


@app.get("/app/state")
def api_status(app_type: AppType):
    if app_type is AppType.water_app:
        water_system_state = get_state_of_water_system()
        if (water_system_state is 0):
            return {"app": app_type ,"state": "STATE_STOPPED"}
        elif (water_system_state is 1):
            return {"app": app_type ,"state": "STATE_RUNNING"}
        elif (water_system_state is 2):
            return {"app": app_type ,"state": "STATE_PAUSED"}
        else:
            return {"app": app_type ,"state": "UNKNOW_STATE"}
    if app_type is AppType.api:
        return {"app": app_type, "state": "plant system api server is obviously up and running..."}
    


@app.get("/app/log")
def get_app_log_fragment(app_type: AppType = AppType.water_app):
    if app_type is AppType.water_app:
        return get_water_system_log_fragment(10)
    if app_type is AppType.api:
        return get_api_log_fragment(10)

@app.get("/water-system/job") 
def change_plant_water_system_job_status(state: bool):
    # todo: return 500 if already running
    if state:
        resume_water_system()
    if not state:
        pause_water_system()


@app.get("/plants/configurations")
def get_all_plants_configurations():
    return plants_configuration.all()

@app.put("/plants/configurations/{plant_id}")
def change_plant_configuration(plant_id: int, plant_conf: PlantConfiguration):
    plants_configuration.update(plant_conf.dict(), doc_ids=[plant_id])

@app.post("/plants/configurations")
def add_plant_configuration(plant_conf: PlantConfiguration):
    plants_configuration.insert(plant_conf.dict())

@app.delete("/plants/configurations/{plant_id}")
def delete_plant_configuration(plant_id: int):
    plants_configuration.remove(where('id') == plant_id)

@app.get("/plants/history")
def get_plant_history(range_start_date: Optional[str], range_end_date: Optional[str]):
    pass




