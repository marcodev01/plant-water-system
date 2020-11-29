#!/usr/bin/env python3

import time
import logging

from typing import Union
from src.model.plant_entry import Plant, PlantSensorEntry
from src.model.plant_configuration import PlantConfiguration

from datetime import datetime
from tinydb import table, Query

from src.waterSystem.components import Relay



########################################################
# helper functions to check water level related values #
########################################################


def is_moisture_level_low(plant: Plant, plant_master_data: PlantConfiguration) -> bool:
    """ compare current mositure level with configured max and min moisture values"""
    logger = logging.getLogger('src.waterSystem')
    if plant_master_data.max_moisture and plant_master_data.min_moisture:
        max_moisture = plant_master_data.max_moisture
        min_moisture = plant_master_data.min_moisture
        moisture = plant.moisture

        if moisture > max_moisture:
            logger.warning(f'Moisture of {plant.name} (ID: {plant.id}) is to high! Measured moisture: {moisture}% (max: {max_moisture})')

        if moisture < min_moisture:
            return True

    return False


def is_conductivity_level_low(plant: Plant, plant_master_data: PlantConfiguration) -> bool:
    """ compare current conductivity level with configured max and min conductivity values"""
    logger = logging.getLogger('src.waterSystem')
    if plant_master_data.max_conductivity and plant_master_data.min_conductivity:
        max_conductivity = plant_master_data.max_conductivity
        min_conductivity = plant_master_data.min_conductivity
        conductivity = plant.conductivity

        if conductivity > max_conductivity:
            logger.warning(f'Conductivity of {plant.name} (ID: {plant.id}) is to high! Measured conductivity: {conductivity} µS/cm (max: {max_conductivity})')

        if conductivity < min_conductivity:
            return True

    return False



###############################################
# helper functions to run a water level check #
###############################################


def find_latest_sensor_history_entry(sensor_history_db: table.Table) -> Union[PlantSensorEntry, None]:
    lastest_entry = None
    for entry in sensor_history_db:
        if lastest_entry is None: # first entry
            lastest_entry = PlantSensorEntry.parse_obj(entry)
        elif datetime.fromisoformat(entry['ts']) > datetime.fromisoformat(lastest_entry.ts):
            lastest_entry = PlantSensorEntry.parse_obj(entry)
    return lastest_entry


def run_water_check(sensor_history_db: table.Table, master_db_plants_conf: table.Table) -> None:
    """ 
    Run check for current water levels of all configured plants 
    and run water pumps for plants with low water level 
    """
    logger = logging.getLogger('src.waterSystem')
    latest_data = find_latest_sensor_history_entry(sensor_history_db)
    for plant in latest_data.plants:
        master_data_query = Query()
        plant_master_data = master_db_plants_conf.get(master_data_query.id == plant.id)
        plant_master_data_obj = PlantConfiguration.parse_obj(plant_master_data)

        if plant_master_data is not None and (is_moisture_level_low(plant, plant_master_data_obj) or is_conductivity_level_low(plant, plant_master_data_obj)):
            logger.info(f'[-WATERING-] Running water pump ({plant_master_data_obj.relay_pin}) for {plant_master_data_obj.plant}. Moisture: {plant.moisture} % (min: {plant_master_data_obj.min_moisture}) / Conductivity: {plant.conductivity} µS/cm (min: {plant_master_data_obj.min_conductivity})')
            run_water_pump(plant_master_data_obj.relay_pin, plant_master_data_obj.water_duration_sec, plant_master_data_obj.water_iterations)
            


######################################
# helper functions to run water pump #
######################################


def run_water_pump(pin: int, pump_duration_sec: float, number_of_runs: int) -> None:
    """ run water pump of specified relay pin and repeat for specfied number of runs """
    relay = Relay(pin)

    for _ in range(number_of_runs):
        time.sleep(1) # default timeout per iteration
        relay.on()
        time.sleep(pump_duration_sec)
        relay.off()
