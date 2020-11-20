#!/usr/bin/env python3
import uuid 
from typing import Optional

from fastapi import FastAPI
from tinydb.queries import where, Query
from datetime import datetime
from src.model.plant_configuration import PlantConfiguration
from src.model.app_type import AppType
from src.db.db_adapter import DbAdapter
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
        return get_log_fragment(10, '../log/api.log')
    if app_type is AppType.api:
        return get_log_fragment(10, '../log/water_system.log')

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
def change_plant_configuration(plant_id: str, plant_conf: PlantConfiguration):
    plants_configuration.update(plant_conf.dict(), where('id') == plant_id)

@app.post("/plants/configurations")
def add_plant_configuration(plant_conf: PlantConfiguration):
    plant_conf.id = uuid.uuid4().hex # generate uniqe id on server side
    plants_configuration.insert(plant_conf.dict())

@app.delete("/plants/configurations/{plant_id}")
def delete_plant_configuration(plant_id: str):
    plants_configuration.remove(where('id') == plant_id)

@app.get("/plants/history")
def get_plant_history(range_start_date: Optional[str], range_end_date: Optional[str]):
    history_entry = Query()

    if range_start_date and range_end_date:
        sensor_history.search(history_entry.ts.test(test_history_range, range_start_date, range_end_date))
    elif range_start_date:
        sensor_history.search(history_entry.ts.test(test_history_range_start, range_start_date))
    elif range_end_date:
        sensor_history.search(history_entry.ts.test(test_history_range_end, range_end_date))
    else:
        sensor_history.all()



####################
# helper functions #
####################

def test_history_range(val: str, start: str, end: str):
    return datetime.fromisoformat(val) > datetime.fromisoformat(start) and datetime.fromisoformat(val) < datetime.fromisoformat(end)

def test_history_range_start(val: str, start: str):
    return datetime.fromisoformat(val) > datetime.fromisoformat(start)

def test_history_range_end(val: str, end: str):
    return datetime.fromisoformat(val) < datetime.fromisoformat(end)

def get_log_fragment(nmb_lines: int, log_file_path: str) -> str:
    log_fragment = ''
    with open(log_file_path) as file:
        for line in (file.readlines() [-nmb_lines:]): 
            log_fragment = log_fragment + line + '\n'
    return log_fragment


