#!/usr/bin/env python3

from src.model.water_system_state import WaterSystemState
from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.events import EVENT_JOB_ERROR, EVENT_JOB_MISSED
from src.waterSystem.water_level_helper import run_water_check, run_water_chron
from src.waterSystem.water_system_db_helper import query_and_persist_sensor_values, clean_up_plant_history

from src.log.logger import setup_logger

# setup custom logger
setup_logger('water.system', '../log/water_system.log')
# setup apscheduler logger
setup_logger('apscheduler', '../log/water_system.log')

QUERY_SENSOR_VALUES_INTERVAL_MIN = 42
RUN_WATER_SYSTEM_INTERVAL_MIN = 60
RUN_WATER_CHRON_INTERVAL_HOURS = 26
RUN_PLANT_DB_CLEAN_UP_INTERVAL_WEEKS = 2

# create scheduler (deafult BackgroundScheduler as daemon)
sched = BackgroundScheduler(daemon=True)

def run_query_and_persist_sensor_values() -> None:
    query_and_persist_sensor_values()

def run_water_system() -> None:
    run_water_check()

def run_water_system_chron() -> None:
    run_water_chron()

def run_plant_db_clean_up() -> None:
    clean_up_plant_history()


def get_state_of_water_system() -> WaterSystemState:
    return WaterSystemState(sched.state)

def pause_water_system() -> None:
    sched.pause()

def resume_water_system() -> None:
    sched.resume()

def shutdown_water_system() -> None:
    sched.shutdown()
    

def job_state_listener(event) -> None:
    if event.code == EVENT_JOB_ERROR:
        print(f'EVENT_JOB_ERROR {event}. EXCEPTION: {event.exception}')
    if event.code == EVENT_JOB_MISSED:
        print(f'EVENT_JOB_MISSED! {event}')


#####################
### job scheduler ###
#####################

def set_up_sched_jobs(chron: bool):
    sched.add_job(run_query_and_persist_sensor_values, 'interval', minutes=QUERY_SENSOR_VALUES_INTERVAL_MIN, id='query_and_persist_sensor_values')

    if chron == True:
        sched.add_job(run_water_system_chron, 'interval', hours=RUN_WATER_CHRON_INTERVAL_HOURS, id='water_chron')
    else:
        sched.add_job(run_water_system, 'interval', minutes=RUN_WATER_SYSTEM_INTERVAL_MIN, id='water_check')

    sched.add_job(run_plant_db_clean_up, 'interval', weeks=RUN_PLANT_DB_CLEAN_UP_INTERVAL_WEEKS, id='run_plant_db_clean_up')
    sched.add_listener(job_state_listener, EVENT_JOB_ERROR | EVENT_JOB_MISSED)

def start_water_system_daemon():
    set_up_sched_jobs(chron=False)
    print('water system script (deamon) is running...')
    sched.start() # run scheduler as deamon (default)

def start_water_chron_daemon():
    set_up_sched_jobs(chron=True)
    print('water chron script (deamon) is running...')
    sched.start() # run scheduler as deamon (default)

if __name__ == '__main__':
    print('started water system as blocking scheduler in main thread...')
    sched = BlockingScheduler() # must run as blocking scheduler if water system runner is running as main program
    set_up_sched_jobs(chron=False)
    print('water system script is running...')
    sched.start()
