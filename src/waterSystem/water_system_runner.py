#!/usr/bin/env python3

from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.events import EVENT_JOB_ERROR, EVENT_JOB_MISSED
from src.waterSystem.water_level_helper import run_water_check
from src.waterSystem.water_system_db_helper import persist_sensor_values

from src.db.db_adapter import DbAdapter

import logging


QUERY_SENSOR_VALUES_INTERVAL_MIN = 42
RUN_WATER_SYSTEM_INTERVAL_MIN = 60

# log configurations
logging.basicConfig(filename='../log/water_system.log',
                    filemode='a', 
                    format='%(asctime)s - %(levelname)s - %(message)s',
                    datefmt='%d-%m-%y %H:%M:%S', 
                    level=logging.INFO)
logger = logging.getLogger('src.waterSystem')

# history db initialisation
plant_db = DbAdapter().plant_db
sensor_history = plant_db.table('sensor_history')
# master data db initialisation
master_data_db = DbAdapter().master_data_db
plants_configuration = master_data_db.table('plants_configuration')

# create scheduler
sched = BlockingScheduler()

def query_sensor_values() -> None:
    persist_sensor_values(sensor_history, plants_configuration)

def run_water_system() -> None:
    run_water_check(sensor_history, plants_configuration)


def get_state_of_water_system() -> int:
    # STATE_STOPPED = 0 / STATE_RUNNING = 1 / STATE_PAUSED = 2
    return sched.state

def pause_water_system() -> None:
    return sched.pause()

def resume_water_system() -> None:
    return sched.resume()
    

def job_state_listener(event) -> None:
    if event.code == EVENT_JOB_ERROR:
        print(f'EVENT_JOB_ERROR: {event.exception}')
    if event.code == EVENT_JOB_MISSED:
        print('EVENT_JOB_MISSED!')


#####################
### job scheduler ###
#####################

if __name__ == '__main__':
    print('water system script is running...')
    sched.add_job(query_sensor_values, 'interval', minutes=QUERY_SENSOR_VALUES_INTERVAL_MIN, id='query_sensor_values')
    sched.add_job(run_water_system, 'interval', minutes=RUN_WATER_SYSTEM_INTERVAL_MIN, id='run_water_check')
    sched.add_listener(job_state_listener, EVENT_JOB_ERROR | EVENT_JOB_MISSED)
    sched.start()
