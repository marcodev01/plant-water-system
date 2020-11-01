#!/usr/bin/env python3

import time
import logging

from typing import Dict, List

from datetime import datetime
from tinydb import table

from components import TemperatureHumiditySensor, TempHumSensorType
from components import MoistureSensor
from components import MifloraSensor
from components import SunlightSensor
from components import Relay


# log configurations
logging.basicConfig(filename='src/database/water_system.log',
                    filemode='a', format='%(asctime)s - %(levelname)s - %(message)s',
                    datefmt='%d-%m-%y %H:%M:%S', level=logging.INFO)
logger = logging.getLogger(__name__) # module logger instance


##############################################################
# helper functions for persisting to sensor history database #
##############################################################

def persist_sensor_values(sensor_history_db: table.Table, master_db_plants_conf: table.Table) -> None:
    """ 
    persist sensor value to sensor history database
    specific sensor parameters/configurations are read out from master database (plants configurations)
    """
    temp_sensor = TemperatureHumiditySensor(channel=16, sensor_type=TempHumSensorType.PRO.value)
    sunlight_sensor = SunlightSensor()

    # query and save values with time stamp to db
    sensor_history_db.insert({
        'ts': datetime.now().isoformat(timespec='seconds'),
        'plants': create_plants_entries_list(master_db_plants_conf),
        'temperature': temp_sensor.read_temperature(),
        'humidity': temp_sensor.read_humidity(),
        'visible_light': sunlight_sensor.readVisible(),
        'UV_index': sunlight_sensor.readUV(),
        'IR_light': sunlight_sensor.readIR(),
    })
    logger.info('Sensor values successfully queried and persistet in db')


def create_plants_entries_list(master_db_plants_conf: table.Table) -> List[Dict[str, any]]:
    """ create a list with all configured plants and its sensor values - sorted by entry id"""

    plants = []
    for plant_conf in master_db_plants_conf:

        # miflora sensor
        if 'mac_adress' in plant_conf:
            # to poll data from miflora sensor a new object has to be created for each poll
            miflora = MifloraSensor(plant_conf['mac_adress'])

            moisture = miflora.read_moisture()
            conductivity = miflora.read_conductivity()
            sunlight = miflora.read_sunlight()
            temperature = miflora.read_temperature()
            battery_level = miflora.get_battery_level()

            plants.append({
                'id': plant_conf.doc_id, 
                'name': plant_conf['plant'], 
                'moisture': moisture, 
                'conductivity': conductivity, 
                'sunlight': sunlight, 
                'temperature': temperature, 
                'batteryLevel': battery_level
                })
        else:  # grove sensor
            mositure_sensor = MoistureSensor(channel=plant_conf['sensor_channel'], sensor_type=plant_conf['sensor_type'])
            moisture = mositure_sensor.read_moisture()

            plants.append({'id': plant_conf.doc_id, 'name': plant_conf['plant'], 'moisture': moisture})

    return sorted(plants, key=lambda plant: plant.get('id'))



########################################################
# helper functions to check water level related values #
########################################################


def is_moisture_level_low(plant: Dict[str, any], plant_master_data: Dict[str, any]) -> bool:
    """ compare current mositure level with configured max and min moisture values"""

    if 'max_moisture' in plant_master_data:
        max_moisture = plant_master_data['max_moisture']
        min_moisture = plant_master_data['min_moisture']

        if plant['moisture'] > max_moisture:
            plant_name = plant['name']
            plant_id = plant['id']
            logger.warning(f'Moisture of {plant_name} - {plant_id} is to high!')

        if plant['moisture'] < min_moisture:
            return True

    return False


def is_conductivity_level_low(plant: Dict[str, any], plant_master_data: Dict[str, any]) -> bool:
    """ compare current conductivity level with configured max and min conductivity values"""

    if 'max_conductivity' in plant_master_data:
        max_conductivity = plant_master_data['max_conductivity']
        min_conductivity = plant_master_data['min_conductivity']

        if plant['conductivity'] > max_conductivity:
            plant_name = plant['name']
            plant_id = plant['id']
            logger.warning(f'Conductivity of {plant_name} - {plant_id} is to high!')

        if plant['conductivity'] < min_conductivity:
            return True

    return False



###############################################
# helper functions to run a water level check #
###############################################


def find_latest_sensor_history_entry(sensor_history_db: table.Table) -> table.Document:
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
    latest_data = find_latest_sensor_history_entry(sensor_history_db)
    for plant in latest_data['plants']:
        plant_master_data = master_db_plants_conf.get(doc_id=int(plant['id']))

        if is_moisture_level_low(plant, plant_master_data) or is_conductivity_level_low(plant, plant_master_data):
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
