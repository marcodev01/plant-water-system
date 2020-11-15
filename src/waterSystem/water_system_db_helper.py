#!/usr/bin/env python3

import logging

from typing import Dict, List, Union

from datetime import datetime
from tinydb import table

from src.waterSystem.components import TemperatureHumiditySensor, TempHumSensorType
from src.waterSystem.components import MoistureSensor
from src.waterSystem.components import MifloraSensor
from src.waterSystem.components import SunlightSensor



##############################################################
# helper functions for persisting to sensor history database #
##############################################################


def persist_sensor_values(sensor_history_db: table.Table, master_db_plants_conf: table.Table) -> None:
    """ 
    persist sensor value to sensor history database
    specific sensor parameters/configurations are read out from master database (plants configurations)
    """
    logger = logging.getLogger('waterSystem')
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


def create_plants_entries_list(master_db_plants_conf: table.Table) -> List[Dict[str, Union[str, int]]]:
    """ create a list with all configured plants and its sensor values - sorted by entry id"""

    plants: List[Dict[str, Union[str, int]]] = []
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
            

    return sorted(plants, key=plant_entry_sorter)

def plant_entry_sorter(plant: Dict[str, Union[str, int]]):
    """ sorter function for plant entries list"""
    plant_id = plant.get('id')
    if not plant_id is None:
        return plant_id
    else:
        return -1