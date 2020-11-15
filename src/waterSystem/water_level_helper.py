#!/usr/bin/env python3

import time
import logging

from typing import Union

from datetime import datetime
from tinydb import table

from src.waterSystem.components import Relay



########################################################
# helper functions to check water level related values #
########################################################


def is_moisture_level_low(plant: table.Document, plant_master_data: table.Document) -> bool:
    """ compare current mositure level with configured max and min moisture values"""
    logger = logging.getLogger('waterSystem')
    if 'max_moisture' in plant_master_data:
        max_moisture = plant_master_data['max_moisture']
        min_moisture = plant_master_data['min_moisture']
        moisture = plant['moisture']

        if moisture > max_moisture:
            plant_name = plant['name']
            plant_id = plant['id']
            logger.warning(f'Moisture of {plant_name} (Id: {plant_id}) is to high!')

        if moisture < min_moisture:
            return True

    return False


def is_conductivity_level_low(plant: table.Document, plant_master_data: table.Document) -> bool:
    """ compare current conductivity level with configured max and min conductivity values"""
    logger = logging.getLogger('waterSystem')
    if 'max_conductivity' in plant_master_data:
        max_conductivity = plant_master_data['max_conductivity']
        min_conductivity = plant_master_data['min_conductivity']
        conductivity = plant['conductivity']

        if conductivity > max_conductivity:
            plant_name = plant['name']
            plant_id = plant['id']
            logger.warning(f'Conductivity of {plant_name} (Id: {plant_id}) is to high!')

        if conductivity < min_conductivity:
            return True

    return False



###############################################
# helper functions to run a water level check #
###############################################


def find_latest_sensor_history_entry(sensor_history_db: table.Table) -> Union[table.Document, None]:
    lastest_entry = None
    for entry in sensor_history_db:
        if lastest_entry is None: # first entry
            lastest_entry = entry
        elif datetime.fromisoformat(entry['ts']) > datetime.fromisoformat(lastest_entry['ts']):
            lastest_entry = entry
    return lastest_entry


def run_water_check(sensor_history_db: table.Table, master_db_plants_conf: table.Table) -> None:
    """ 
    Run check for current water levels of all configured plants 
    and run water pumps for plants with low water level 
    """
    logger = logging.getLogger('waterSystem')
    latest_data = find_latest_sensor_history_entry(sensor_history_db)
    for plant in latest_data['plants']:
        plant_master_data = master_db_plants_conf.get(doc_id=int(plant['id']))

        if plant_master_data is not None and (is_moisture_level_low(plant, plant_master_data) or is_conductivity_level_low(plant, plant_master_data)):
            plant_config = master_db_plants_conf.get(doc_id=int(plant['id']))
            run_water_pump(plant_config['relay_pin'], plant_config['water_duration_sec'], plant_config['water_iterations'])
            
            plant_name = plant_config['plant']
            logger.info(f'Run water pump for {plant_name}')


######################################
# helper functions to run water pump #
######################################


def run_water_pump(pin: int, pump_duration_sec: float, number_of_runs: int) -> None:
    """ run water pump of specified relay pin and repeat for specfied number of runs """
    relay = Relay(pin)

    for _ in range(number_of_runs):
        relay.on()
        time.sleep(pump_duration_sec)
        relay.off()
