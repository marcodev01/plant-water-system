#!/usr/bin/env python3

import logging
import time

from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.events import EVENT_JOB_ERROR, EVENT_JOB_EXECUTED, EVENT_JOB_MISSED
from components import Relay
from components import TemperatureHumiditySensor, TempHumSensorType
from components import MoistureSensor
from components import MifloraSensor
from tinydb import TinyDB
from datetime import datetime

# log configurations
logging.basicConfig(filename='src/database/water_system.log',
                    filemode='a', format='%(asctime)s - %(levelname)s - %(message)s',
                    datefmt='%d-%m-%y %H:%M:%S', level=logging.INFO)

# history db initialisation
plant_db = TinyDB('src/database/plant_history.json')
sensor_history = plant_db.table('sensor_history')
# master data db initialisation
master_data_db = TinyDB('src/database/master_data.json')
plants_conf = master_data_db.table('plants_configuration')


def query_sensor_values():
    temp_sensor = TemperatureHumiditySensor(channel=16, sensor_type=TempHumSensorType.PRO.value)

    # query and save values with time stamp to db
    sensor_history.insert({
        'ts': datetime.now().isoformat(timespec='seconds'),
        'plants': create_plants_entries_list(),
        'temperatureGeneral': temp_sensor.read_temperature(),
        'humidityGeneral': temp_sensor.read_humidity()
    })
    logging.info('Sensor values successfully persistet in db')


def create_plants_entries_list():

    plants = []
    for plant in plants_conf:

        # miflora sensor
        if 'mac_adress' in plant:
            # to poll data from miflora sensor a new object has to be created for each poll
            miflora = MifloraSensor(plant['mac_adress'])

            moisture = miflora.read_moisture()
            conductivity = miflora.read_conductivity()
            sunlight = miflora.read_sunlight()
            temperature = miflora.read_temperature()
            battery_level = miflora.get_battery_level()

            plants.append({
                'id': plant.doc_id, 
                'name': plant['plant'], 
                'moisture': moisture, 
                'conductivity': conductivity, 
                'sunlight': sunlight, 
                'temperature': temperature, 
                'batteryLevel': battery_level
                })
        else:  # grove sensor
            mositure_sensor = MoistureSensor(channel=plant['sensor_channel'], sensor_type=plant['sensor_type'])
            moisture = mositure_sensor.read_moisture()

            plants.append({'id': plant.doc_id, 'name': plant['plant'], 'moisture': moisture})

    return sorted(plants, key=lambda plant: plant.get('id'))


def run_water_check():
    latest_data = find_latest_entry()
    for plant in latest_data['plants']:
        if check_moisture_level(plant) or check_conductivity_level(plant):
            plant_config = plants_conf.get(doc_id=int(plant['id']))
            run_water_pump(plant_config['relay_pin'], plant_config['water_duration_sec'], plant_config['water_iterations'])


def check_moisture_level(plant):
    plant_master_data = plants_conf.get(doc_id=int(plant['id']))

    if 'max_moisture' in plant_master_data:
        max_moisture = plant_master_data['max_moisture']
        min_moisture = plant_master_data['min_moisture']

        if plant['moisture'] > max_moisture:
            plant_name = plant['name']
            plant_id = plant['id']
            logging.warning(f'Moisture of {plant_name} - {plant_id} is to high!')

        if plant['moisture'] < min_moisture:
            return True

    return False


def check_conductivity_level(plant):
    plant_master_data = plants_conf.get(doc_id=int(plant['id']))

    if 'max_conductivity' in plant_master_data:
        max_conductivity = plant_master_data['max_conductivity']
        min_conductivity = plant_master_data['min_conductivity']

        if plant['conductivity'] > max_conductivity:
            plant_name = plant['name']
            plant_id = plant['id']
            logging.warning(f'Conductivity of {plant_name} - {plant_id} is to high!')

        if plant['conductivity'] < min_conductivity:
            return True

    return False


def find_latest_entry():
    lastest_entry = None
    for entry in sensor_history:
        if lastest_entry is None:
            lastest_entry = entry
        elif datetime.fromisoformat(entry['ts']) > datetime.fromisoformat(lastest_entry['ts']):
            lastest_entry = entry
    return lastest_entry


def run_water_pump(pin, pump_duration_sec, number_of_runs):
    relay = Relay(pin)

    for _ in range(number_of_runs):
        relay.on()
        time.sleep(pump_duration_sec)
        relay.off()


def job_state_listener(event):
    if event.code == EVENT_JOB_ERROR:
        print(f'An error occured during job please check the logs! {event.exception}')
        logging.error(f'EVENT_JOB_ERROR: {event.exception}')
    elif event.code == EVENT_JOB_MISSED:
        logging.warning('EVENT_JOB_MISSED: A Job exceution missed!')
    elif event.code == EVENT_JOB_EXECUTED:
        print(f'DONE {datetime.now()}')
    else:
        print(f'UNKNOWN_EVENT: An unknown event occured please check the logs! {event}')
        logging.warning(f'UNKNOWN_EVENT: {event}')


if __name__ == '__main__':
    print('water system is running...')
    sched = BlockingScheduler()
    sched.add_job(query_sensor_values, 'interval', minutes=60, id='query_sensor_values')
    sched.add_job(run_water_check, 'interval', minutes=90, id='run_water_check')
    sched.add_listener(job_state_listener, EVENT_JOB_EXECUTED | EVENT_JOB_ERROR | EVENT_JOB_MISSED)
    sched.start()
