#!/usr/bin/env python3
from src.model.water_system_state import WaterSystemState
from src.log.logger import setup_logger
from src.model.plant_entry import PlantSensorEntry
import uuid 
from uuid import UUID
from typing import List, Optional

from fastapi import FastAPI, Query as FastAPIQuery, Path, Body, status, Response, HTTPException
from tinydb.queries import where, Query
from datetime import date
from src.model.plant_configuration import PlantConfiguration
from src.model.app_type import AppType
from src.db.db_adapter import DbAdapter
from src.waterSystem.water_system_runner import get_state_of_water_system, resume_water_system, pause_water_system, start_water_system_daemon

# setup uvicorn loggers
setup_logger('uvicorn.error', '../log/api.log')
setup_logger('uvicorn.access', '../log/api.log')

# history db initialisation
plant_db = DbAdapter().plant_db
sensor_history = plant_db.table('sensor_history')
# master data db initialisation
master_data_db = DbAdapter().master_data_db
plants_configuration = master_data_db.table('plants_configuration')

# start api
app = FastAPI()
# start water system demaon directly from same thread as api to ensure access to apscheduler environment 
start_water_system_daemon()


@app.get("/app/state", tags=["app"])
def api_status(
    app_type: AppType = FastAPIQuery(..., title="ApplicationType", description="Application type to be queried: `water_app` OR `api`")
):
    """ 
    Get the current state of app:

    _water_system_:
    - **STATE_STOPPED**
    - **STATE_RUNNING**
    - **STATE_PAUSED**
    - **UNKNOW_STATE**

    _api_:
    - **200 OK**: api is running
    - **No Response**: api is not running
    """
    if app_type is AppType.water_app:
        water_system_state = get_state_of_water_system()
        if (water_system_state is WaterSystemState.STATE_STOPPED.value):
            return {"app": app_type ,"state": WaterSystemState.STATE_STOPPED.name}
        elif (water_system_state is WaterSystemState.STATE_RUNNING.value):
            return {"app": app_type ,"state": WaterSystemState.STATE_RUNNING.name}
        elif (water_system_state is WaterSystemState.STATE_PAUSED.value):
            return {"app": app_type ,"state": WaterSystemState.STATE_PAUSED.name}
        else:
            return {"app": app_type ,"state": "UNKNOW_STATE"}
    if app_type is AppType.api:
        return {"app": app_type, "state": "plant system api server is up and running..."}
    


@app.get("/app/log", tags=["app"])
def get_app_log_fragment(
    app_type: AppType = FastAPIQuery(AppType.water_app, title="ApplicationType", description="Log file of application type: `water_app` OR `api`"),
    log_size: int = FastAPIQuery(20, title="LogSize", description="Number of the last log entries to request")
):
    """
    Get log file entries of app.
    By default a fragment of the latest **10 log entries** will be supplied
    """
    if app_type is AppType.water_app:
        return get_log_fragment(log_size, '../log/water_system.log')
    if app_type is AppType.api:
        return get_log_fragment(log_size, '../log/api.log')


@app.get("/water-system/job", tags=["app"]) 
def pause_or_resume_water_system(response: Response, state: bool = FastAPIQuery(..., title="waterSystemState", description="change state of water system `on` OR `off`")):
    """
    Pause water system by **off** or resume water system by **on**
    
    Response is either **HTTP 200** if state successfully changed or **HTTP 500** if water system is either already in requested state or in an unexpected state
    """
    water_system_state = get_state_of_water_system()
    if state: # resume water system
        if water_system_state is WaterSystemState.STATE_PAUSED.value:
            resume_water_system()
            response.status_code = status.HTTP_200_OK
        else:
            if water_system_state is WaterSystemState.STATE_RUNNING.value:
                raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR , detail="Water system already running..")
            else:
                raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR , detail="Water system is in an unexpected state..")
    if not state: # pause water system
        if water_system_state is WaterSystemState.STATE_RUNNING.value:
            pause_water_system()
            response.status_code = status.HTTP_200_OK
        else:
            if water_system_state is WaterSystemState.STATE_PAUSED.value:
                raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR , detail="Water system already paused..")
            else:
                raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR , detail="Water system is in an unexpected state..")

     

@app.get("/plants/configuration", response_model=List[PlantConfiguration], tags=["plants configuration"])
def get_all_plants_configurations():
    """ Get all plants configurations as list """
    return plants_configuration.all()


@app.put("/plants/configuration/{plant_id}", tags=["plants configuration"])
def update_plant_configuration(
    plant_id: UUID = Path(..., title="ID of plant to change configuration"), 
    plant_conf: PlantConfiguration = Body(..., title="updated plant configuration", example={"id": "abc123", "sensor_type": "moisture_capacitve", "sensor_channel": 2, "plant": "My Plant", "relay_pin": 5, "water_duration_sec": 3, "water_iterations": 1, "max_moisture": 90, "min_moisture": 42 })
):
    """ Updates an existing plant configuration"""
    plants_configuration.update(plant_conf.dict(exclude_none=True), where('id') == plant_id) # TODO: handle if requested plant not available


@app.post("/plants/configuration", response_model=PlantConfiguration, status_code=status.HTTP_201_CREATED, tags=["plants configuration"])
def add_plant_configuration(plant_conf: PlantConfiguration = Body(..., title="new plant configuration", example={"sensor_type": "moisture_capacitve", "sensor_channel": 2, "plant": "My Plant", "relay_pin": 5, "water_duration_sec": 3, "water_iterations": 1, "max_moisture": 90, "min_moisture": 42 })):
    """ 
    Add a new plant configuration

    Note: **uuid** for newly created plant configuration is **generated on server side**. The Response contains the new plant configuration including generated uuid.
    """
    plant_conf.id = uuid.uuid4().hex # generate uniqe id on server side
    plants_configuration.insert(plant_conf.dict(exclude_none=True))
    return plant_conf


@app.delete("/plants/configuration/{plant_id}", tags=["plants configuration"])
def delete_plant_configuration(plant_id: UUID = Path(..., title="ID of plant configuration to delete")):
    """ Delete an existing plant configuration """
    plants_configuration.remove(where('id') == plant_id) # TODO: handle if requested plant not available


@app.get("/plants/history", response_model=List[PlantSensorEntry], tags=["plants history"])
def get_plant_history(
    range_start_date: Optional[str] = FastAPIQuery(None, description="Note: start date is assumed to be in ISO format (YYYY-MM-DD)",regex="^([0-9]{4})(-)(1[0-2]|0[1-9])\2(3[01]|0[1-9]|[12][0-9])$"),
    range_end_date: Optional[str]= FastAPIQuery(None, description="Note: end date is assumed to be in ISO format (YYYY-MM-DD)", regex="^([0-9]{4})(-)(1[0-2]|0[1-9])\2(3[01]|0[1-9]|[12][0-9])$")
):
    """ 
    Get entries of plant sensor history db.

    The query can be narrowed as follows by query params:
    - **range_start_date** AND **range_end_date**: Gets all entries between range_start_date and range_end_date
    - **range_start_date**: Gets all entries which are newer than range_start_date
    - **range_end_date**: Gets all entries which are older than range_end_date
    - **NO QUERY PARAM**: Gets all entries of sensor history db
    """
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
            log_fragment = log_fragment + line
    return log_fragment


