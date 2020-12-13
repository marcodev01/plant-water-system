#!/usr/bin/env python3

import logging
from tinydb.queries import Query
from src.model.plant_entry import PlantSensorEntry, Plant
from src.model.plant_configuration import PlantConfiguration

from typing import List

from datetime import datetime
from tinydb import table

from src.waterSystem.components import TemperatureHumiditySensor, TempHumSensorType
from src.waterSystem.components import MoistureSensor
from src.waterSystem.components import MifloraSensor
from src.waterSystem.components import SunlightSensor

logger = logging.getLogger('water.system')

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
    
    plant_sensor_entry_obj = PlantSensorEntry(
        ts=datetime.now().isoformat(timespec='seconds'),
        plants=create_plants_entries_list(master_db_plants_conf),
        temperature=temp_sensor.read_temperature(),
        humidity=temp_sensor.read_humidity(),
        visible_light=sunlight_sensor.readVisible(),
        UV_index=sunlight_sensor.readUV(),
        IR_light=sunlight_sensor.readIR()
    )

    # query and save values with time stamp to db
    sensor_history_db.insert(plant_sensor_entry_obj.dict())
    logger.info('Sensor values successfully queried and persistet in db')


def create_plants_entries_list(master_db_plants_conf: table.Table) -> List[Plant]:
    """ create a list with all configured plants and its sensor values - sorted by entry doc_id"""

    plants: List[Plant] = []
    for plant_conf in master_db_plants_conf:

        # parse plant_conf Document to object
        plant_configuration_obj = PlantConfiguration.parse_obj(plant_conf)
        # miflora sensor
        if plant_configuration_obj.mac_adress:
            # to poll data from miflora sensor a new object has to be created for each poll
            miflora = MifloraSensor(plant_configuration_obj.mac_adress)

            moisture = miflora.read_moisture()
            conductivity = miflora.read_conductivity()
            sunlight = miflora.read_sunlight()
            temperature = miflora.read_temperature()
            battery_level = miflora.get_battery_level()

            plants.append(Plant(
                id=plant_configuration_obj.id, 
                name=plant_configuration_obj.plant,
                moisture=moisture, 
                conductivity=conductivity, 
                sunlight=sunlight, 
                temperature=temperature, 
                batteryLevel=battery_level))
        else:  # grove sensor
            mositure_sensor = MoistureSensor(channel=plant_configuration_obj.sensor_channel, sensor_type=plant_configuration_obj.sensor_type)
            moisture = mositure_sensor.read_moisture()

            plants.append(Plant(id=plant_configuration_obj.id, name=plant_configuration_obj.plant, moisture=moisture))
            
    return sorted(plants, key=lambda p: plant_entry_sorter(p, master_db_plants_conf))

def plant_entry_sorter(plant: Plant, master_db_plants_conf: table.Table) -> int:
    """ sorter function for plant entries list. Sort by doc_id"""
    plant_query = Query()
    plant_entry = master_db_plants_conf.get(plant_query.id == plant.id)
    plant_seq = plant_entry.doc_id
    if not plant_seq is None:
        return plant_seq
    else:
        return -1