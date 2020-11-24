#!/usr/bin/env python3
from src.model.plant_entry import PlantSensorEntry
import uuid 
from uuid import UUID
from typing import List, Optional

from fastapi import FastAPI, Query as FastAPIQuery, Path, Body, status, Response
from tinydb.queries import where, Query
from datetime import date
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
logger = logging.getLogger('src.api')

# history db initialisation
plant_db = DbAdapter().plant_db
sensor_history = plant_db.table('sensor_history')
# master data db initialisation
master_data_db = DbAdapter().master_data_db
plants_configuration = master_data_db.table('plants_configuration')

app = FastAPI()


@app.get("/app/state")
def api_status(
    app_type: AppType = FastAPIQuery(..., title="ApplicationType", 
    description="Application type for current state - eihter water system (STATE_STOPPED / STATE_RUNNING / STATE_PAUSED) or api (if response is 200 OK api is runnning)")
):
    if app_type is AppType.water_app:
        water_system_state = get_state_of_water_system()
        if (water_system_state is 0):
            return {"app": app_type ,"state": "STATE_STOPPED"} # TODO app state type model
        elif (water_system_state is 1):
            return {"app": app_type ,"state": "STATE_RUNNING"}
        elif (water_system_state is 2):
            return {"app": app_type ,"state": "STATE_PAUSED"}
        else:
            return {"app": app_type ,"state": "UNKNOW_STATE"}
    if app_type is AppType.api:
        return {"app": app_type, "state": "plant system api server is obviously up and running..."}
    


@app.get("/app/log")
def get_app_log_fragment(app_type: AppType = FastAPIQuery(
    AppType.water_app, title="ApplicationType", description="Application type for latest log file entries (either water system or api)")
):
    if app_type is AppType.water_app:
        return get_log_fragment(10, '../log/api.log')
    if app_type is AppType.api:
        return get_log_fragment(10, '../log/water_system.log')

@app.get("/water-system/job") 
def pause_or_resume_water_system(response: Response, state: bool = FastAPIQuery(..., title="waterSystemState", description="change state of water system by setting state `on` or `off`")):
    if state:
        if get_state_of_water_system() is 2: # TODO Enum for water system state
            resume_water_system()
            response.status_code = status.HTTP_200_OK
        else:
            # already running or unexpected state!
            response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR 
    if not state:
        if get_state_of_water_system() is 1:
            pause_water_system()
            response.status_code = status.HTTP_200_OK
        else:
            # already paused or unexpected state!
            response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
     


@app.get("/plants/configuration", response_model=List[PlantConfiguration])
def get_all_plants_configurations():
    return plants_configuration.all()

@app.put("/plants/configuration/{plant_id}")
def update_plant_configuration(
    plant_id: UUID = Path(..., title="ID of plant to change configuration"), 
    plant_conf: PlantConfiguration = Body(..., title="updated plant configuration", example={"id": "abc123", "sensor_type": "moisture_capacitve", "sensor_channel": 2, "plant": "My Plant", "relay_pin": 5, "water_duration_sec": 3, "water_iterations": 1, "max_moisture": 90, "min_moisture": 42 })
):
    plants_configuration.update(plant_conf.dict(), where('id') == plant_id)

@app.post("/plants/configuration", response_model=PlantConfiguration, status_code=status.HTTP_201_CREATED)
def add_plant_configuration(plant_conf: PlantConfiguration = Body(..., title="add new plant configuration", description="Note: ID for new plant configuration is generated on server side", example={"sensor_type": "moisture_capacitve", "sensor_channel": 2, "plant": "My Plant", "relay_pin": 5, "water_duration_sec": 3, "water_iterations": 1, "max_moisture": 90, "min_moisture": 42 })):
    plant_conf.id = uuid.uuid4().hex # generate uniqe id on server side
    plants_configuration.insert(plant_conf.dict())
    return plant_conf

@app.delete("/plants/configuration/{plant_id}")
def delete_plant_configuration(plant_id: UUID = Path(..., title="ID of plant to delete configuration")):
    plants_configuration.remove(where('id') == plant_id)

@app.get("/plants/history", response_model=List[PlantSensorEntry])
def get_plant_history(
    range_start_date: Optional[str] = FastAPIQuery(None, title="start date of history entries to query", description="Note: start date is assumed to be in ISO format (YYYY-MM-DD)",regex="^([0-9]{4})(-)(1[0-2]|0[1-9])\2(3[01]|0[1-9]|[12][0-9])$"),
    range_end_date: Optional[str]= FastAPIQuery(None, title="end date of history entries to query", description="Note: end date is assumed to be in ISO format (YYYY-MM-DD)", regex="^([0-9]{4})(-)(1[0-2]|0[1-9])\2(3[01]|0[1-9]|[12][0-9])$")
):
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

def test_history_range(val: str, start: str, end: str) -> bool:
    return date.fromisoformat(val) > date.fromisoformat(start) and date.fromisoformat(val) < date.fromisoformat(end)

def test_history_range_start(val: str, start: str) -> bool:
    return date.fromisoformat(val) > date.fromisoformat(start)

def test_history_range_end(val: str, end: str) -> bool:
    return date.fromisoformat(val) < date.fromisoformat(end)

def get_log_fragment(nmb_lines: int, log_file_path: str) -> str:
    log_fragment = ''
    with open(log_file_path) as file:
        for line in (file.readlines() [-nmb_lines:]): 
            log_fragment = log_fragment + line + '\n'
    return log_fragment


