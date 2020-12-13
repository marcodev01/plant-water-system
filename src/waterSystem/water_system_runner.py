#!/usr/bin/env python3

from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.events import EVENT_JOB_ERROR, EVENT_JOB_MISSED
from src.waterSystem.water_level_helper import run_water_check
from src.waterSystem.water_system_db_helper import query_and_persist_sensor_values

from src.log.logger import setup_logger

# setup custom logger
setup_logger('water.system', '../log/water_system.log')
# setup apscheduler logger
setup_logger('apscheduler', '../log/water_system.log')

QUERY_SENSOR_VALUES_INTERVAL_MIN = 42
RUN_WATER_SYSTEM_INTERVAL_MIN = 60

# create scheduler
sched = BlockingScheduler()

def run_query_and_persist_sensor_values() -> None:
    query_and_persist_sensor_values()

def run_water_system() -> None:
    run_water_check()


def get_state_of_water_system() -> int:
    """STATE_STOPPED = 0 / STATE_RUNNING = 1 / STATE_PAUSED = 2"""
    return sched.state

def pause_water_system() -> None:
    return sched.pause()

def resume_water_system() -> None:
    return sched.resume()
    

def job_state_listener(event) -> None:
    if event.code == EVENT_JOB_ERROR:
        print(f'EVENT_JOB_ERROR {event}. EXCEPTION: {event.exception}')
    if event.code == EVENT_JOB_MISSED:
        print(f'EVENT_JOB_MISSED! {event}')


#####################
### job scheduler ###
#####################

if __name__ == '__main__':
    print('water system script is running...')
    sched.add_job(run_query_and_persist_sensor_values, 'interval', minutes=QUERY_SENSOR_VALUES_INTERVAL_MIN, id='query_and_persist_sensor_values')
    sched.add_job(run_water_system, 'interval', minutes=RUN_WATER_SYSTEM_INTERVAL_MIN, id='water_check')
    sched.add_listener(job_state_listener, EVENT_JOB_ERROR | EVENT_JOB_MISSED)
    sched.start()
