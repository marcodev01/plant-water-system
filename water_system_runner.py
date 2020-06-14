#!/usr/bin/env python3

import logging

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
relay = Relay(pin=5)
temp_sensor = TemperatureHumiditySensor(channel=16, sensor_type=TempHumSensorType.PRO.value)
moister_standard = MoistureSensor(channel=0, sensor_type=MoistureSensorType.STANDARD.value)
moister_capacitive = MoistureSensor(channel=2, sensor_type=MoistureSensorType.CAPACITIVE.value)

# db initialisation
db = TinyDB('database/plant_db.json')
sensor_table = db.table('sensor_history')


def query_sensor_values():
    moisture_1_percent = moister_standard.read_moisture() / moister_standard.
    moisture_2_percent = moister_capacitive.read_moisture()
    
    # to poll data from miflora sensor a new object has to be created for each poll
    miflora_sensor = MifloraSensor("80:EA:CA:89:60:A7")
    
    # query and save values with time stamp to db
    sensor_table.insert({
        'ts': datetime.now().isoformat(timespec='seconds'),
        'plants': [
            {'name': 'Aji Lemon Drop', 'moisture': moisture_1_percent},
            {'name': 'Peperoncino Veena', 'moisture': moisture_2_percent},
            {'name': 'Jalapeno', 'moisture': miflora_sensor.read_moisture(), 'conductivity': miflora_sensor.read_conductivity(),
             'sunlight': miflora_sensor.read_sunlight(), 'temperature': miflora_sensor.read_temperature(),
             'batteryLevel': miflora_sensor.get_battery_level()}
        ],
        'temperatureGeneral': temp_sensor.read_temperature(),
        'humidityGeneral': temp_sensor.read_humidity()
    })
    logging.info('Sensor values successfully persistet in db')


def job_state_listener(event):
    if event.code == EVENT_JOB_ERROR:
        print(f'An error occured during job please check the logs! {event.exception}')
        logging.error(f'EVENT_JOB_ERROR: {event.exception}')
    elif event.code == EVENT_JOB_MISSED:
        logging.warning('EVENT_JOB_MISSED: A Job exceution missed!')
    elif event.code == EVENT_JOB_EXECUTED:
        print(f'DONE {query_sensors_ts}')
    else:
        print(f'UNKNOWN_EVENT: An unknown event occured please check the logs! {event}')
        logging.warning(f'UNKNOWN_EVENT: {event}')


if __name__ == '__main__':
    print('water system is running...')
    sched = BlockingScheduler()
    sched.add_job(query_sensor_values, 'interval', seconds=5, id='query_sensor_values')
    sched.add_listener(job_state_listener, EVENT_JOB_EXECUTED | EVENT_JOB_ERROR | EVENT_JOB_MISSED)
    sched.start()
