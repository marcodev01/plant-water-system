#!/usr/bin/env python3

import logging
import time

from typing import Union
from src.model.plant_entry import Plant, PlantSensorEntry
from src.model.plant_configuration import PlantConfiguration

from datetime import datetime
from tinydb import Query
from src.db.db_adapter import DbAdapter, SENSOR_HISTORY_TABLE_NAME, PLANTS_CONFIGURATION_TABLE_NAME

from src.waterSystem.components import Relay

logger = logging.getLogger('water.system')

########################################################
# helper functions to check water level related values #
########################################################


def __is_moisture_level_low(plant: Plant, plant_configuration_obj: PlantConfiguration) -> bool:
    """ compare current mositure level with configured max and min moisture values"""
    if plant_configuration_obj.max_moisture and plant_configuration_obj.min_moisture:
        max_moisture = plant_configuration_obj.max_moisture
        min_moisture = plant_configuration_obj.min_moisture
        moisture = plant.moisture

        if moisture > max_moisture:
            logger.warning(f'Moisture of {plant.name} (ID: {plant.id}) is to high! Measured moisture: {moisture}% (max: {max_moisture})')

        if moisture < min_moisture:
            return True

    return False


def __is_conductivity_level_low(plant: Plant, plant_configuration_obj: PlantConfiguration) -> bool:
    """ compare current conductivity level with configured max and min conductivity values"""
    if plant_configuration_obj.max_conductivity and plant_configuration_obj.min_conductivity:
        max_conductivity = plant_configuration_obj.max_conductivity
        min_conductivity = plant_configuration_obj.min_conductivity
        conductivity = plant.conductivity

        if conductivity > max_conductivity:
            logger.warning(f'Conductivity of {plant.name} (ID: {plant.id}) is to high! Measured conductivity: {conductivity} µS/cm (max: {max_conductivity})')

        if conductivity < min_conductivity:
            return True

    return False



###############################################
# helper functions to run a water level check #
###############################################


def __find_latest_sensor_history_entry() -> Union[PlantSensorEntry, None]:

    # history db connection
    plant_db = DbAdapter().plant_db
    sensor_history_db = plant_db.table(SENSOR_HISTORY_TABLE_NAME)

    lastest_entry = None
    for entry in sensor_history_db:
        if lastest_entry is None: # first entry
            lastest_entry = PlantSensorEntry.parse_obj(entry)
        elif datetime.fromisoformat(entry['ts']) > datetime.fromisoformat(lastest_entry.ts):
            lastest_entry = PlantSensorEntry.parse_obj(entry)
    return lastest_entry


def run_water_check() -> None:
    """ 
    Run check for current water levels of all configured plants 
    and run water pumps for plants with low water level 
    """

    # master data db connection
    master_data_db = DbAdapter().master_data_db
    plants_master_data_db = master_data_db.table(PLANTS_CONFIGURATION_TABLE_NAME)

    latest_data = __find_latest_sensor_history_entry()
    for plant in latest_data.plants:
        master_data_query = Query()
        plant_master_data = plants_master_data_db.get(master_data_query.id == plant.id)
        plant_master_data_obj = PlantConfiguration.parse_obj(plant_master_data)

        has_low_moisture_level = __is_moisture_level_low(plant, plant_master_data_obj)
        has_low_conductivity_level = __is_conductivity_level_low(plant, plant_master_data_obj)

        if plant_master_data is not None and (has_low_moisture_level or has_low_conductivity_level):
            if has_low_moisture_level:
                logger.info(f'[-WATERING-] Running water pump ({plant_master_data_obj.relay_pin}) for {plant_master_data_obj.plant}. Moisture: {plant.moisture} % (min: {plant_master_data_obj.min_moisture})')
            if has_low_conductivity_level:
                logger.info(f'[-WATERING-] Running water pump ({plant_master_data_obj.relay_pin}) for {plant_master_data_obj.plant}. Conductivity: {plant.conductivity} µS/cm (min: {plant_master_data_obj.min_conductivity})')
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
