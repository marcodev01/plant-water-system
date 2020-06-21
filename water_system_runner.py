#!/usr/bin/env python3

import logging
import json
import time

from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.events import EVENT_JOB_ERROR, EVENT_JOB_EXECUTED, EVENT_JOB_MISSED
from components import Relay
from components import TemperatureHumiditySensor, TempHumSensorType
from components import MoistureSensor, MoistureSensorType
from components import MifloraSensor
from tinydb import TinyDB
from datetime import datetime

# configurations
logging.basicConfig(filename='database/water_system.log',
                    filemode='a', format='%(asctime)s - %(levelname)s - %(message)s',
                    datefmt='%d-%m-%y %H:%M:%S', level=logging.INFO)

# initialisation of sensor components
temp_sensor = TemperatureHumiditySensor(channel=16, sensor_type=TempHumSensorType.PRO.value)
moister_standard = MoistureSensor(channel=0, sensor_type=MoistureSensorType.STANDARD.value)
moister_capacitive = MoistureSensor(channel=2, sensor_type=MoistureSensorType.CAPACITIVE.value)

# db initialisation
db = TinyDB('database/plant_db.json')
sensor_history = db.table('sensor_history')

# load master data
with open('database/master_data.json') as data_file:
    master_data = json.load(data_file)


def query_sensor_values():
    moisture_1_percent = moister_standard.read_moisture()
    moisture_2_percent = moister_capacitive.read_moisture()

    # to poll data from miflora sensor a new object has to be created for each poll
    miflora_sensor = MifloraSensor("80:EA:CA:89:60:A7")

    # query and save values with time stamp to db
    sensor_history.insert({
        'ts': datetime.now().isoformat(timespec='seconds'),
        'plants': [
            {'id': '1', 'name': 'Aji Lemon Drop', 'moisture': moisture_1_percent},
            {'id': '2', 'name': 'Peperoncino Veena', 'moisture': moisture_2_percent},
            {'id': '3', 'name': 'Jalapeno', 'moisture': miflora_sensor.read_moisture(), 'conductivity': miflora_sensor.read_conductivity(),
             'sunlight': miflora_sensor.read_sunlight(), 'temperature': miflora_sensor.read_temperature(),
             'batteryLevel': miflora_sensor.get_battery_level()}
        ],
        'temperatureGeneral': temp_sensor.read_temperature(),
        'humidityGeneral': temp_sensor.read_humidity()
    })
    logging.info('Sensor values successfully persistet in db')


def run_water_check():
    latest_data = find_latest_entry()
    for plant in latest_data['plants']:
        if check_moisture_level(plant) or check_conductivity_level(plant):
            run_water_pump(master_data[plant['id']]['relay_pin'])


def check_moisture_level(plant):
    max_moisture = master_data[plant['id']]['max_moisture']
    min_moisture = master_data[plant['id']]['min_moisture']

    if plant['moisture'] > max_moisture:
        plant_name = plant['name']
        plant_id = plant ['id']
        logging.warning(f'Moisture of {plant_name} id: {plant_id} is to high!')

    if plant['moisture'] < min_moisture:
        return True
    else:
        return False


def check_conductivity_level(plant):
    if 'max_conductivity' in master_data[plant['id']]:
        max_conductivity = master_data[plant['id']]['max_conductivity']
        min_conductivity = master_data[plant['id']]['min_conductivity']

        if plant['conductivity'] > max_conductivity:
            plant_name = plant['name']
            plant_id = plant ['id']
            logging.warning(f'Conductivity of {plant_name} id: {plant_id} is to high!')

        if plant['conductivity'] < min_conductivity:
            return True
    else:
        return False


def find_latest_entry():
    lastest_entry = None
    for entry in sensor_history:
        if lastest_entry is None:
            lastest_entry = entry
        elif datetime.fromisoformat(entry['ts']) > datetime.fromisoformat(lastest_entry['ts']):
            lastest_entry = entry
    return lastest_entry


def run_water_pump(pin):
    relay = Relay(pin)
    relay.on()
    time.sleep(4)
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
    sched.add_job(query_sensor_values, 'interval', seconds=5, id='query_sensor_values')
    sched.add_job(run_water_check, 'interval', seconds=8, id='run_water_check')
    sched.add_listener(job_state_listener, EVENT_JOB_EXECUTED | EVENT_JOB_ERROR | EVENT_JOB_MISSED)
    sched.start()
