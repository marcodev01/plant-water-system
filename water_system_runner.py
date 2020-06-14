#!/usr/bin/env python3

from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.events import EVENT_JOB_ERROR, EVENT_JOB_EXECUTED, EVENT_JOB_MISSED  # noqa: E501
from components import Relay
from components import TemperatureHumiditySensor, TempHumSensorType
from components import MoistureSensor, MoistureSensorType
from components import MifloraSensor
from tinydb import TinyDB, Query
from datetime import datetime

# components initzialisation
relay = Relay(pin=5)
temp_sensor = TemperatureHumiditySensor(channel=16, sensor_type=TempHumSensorType.PRO.value)  # noqa: E501
moister_standard = MoistureSensor(channel=0, sensor_type=MoistureSensorType.STANDARD.value)  # noqa: E501
moister_capacitive = MoistureSensor(channel=2, sensor_type=MoistureSensorType.CAPACITIVE.value)  # noqa: E501
miflora_sensor = MifloraSensor("80:EA:CA:89:60:A7")
db = TinyDB('database/plant_db.json')
sensor_table = db.table('sensor_logs')


def query_sesnor_values():
    current_datetime = datetime.now()
    current_iso_datetime = current_datetime.isoformat(timespec='seconds')

    db.insert({
        'ts': current_iso_datetime,
        'plants': [
            {'name': 'Aji Lemon Drop', 'moisture': moister_standard.read_moisture()},
            {'name': 'Peperoncino Veena', 'moisture': moister_capacitive.read_moisture()},
            {'name': 'Jalapeno', 'moisture': miflora_sensor.read_moisture(), 'conductivity': miflora_sensor.read_conductivity(), 
            'sunlight': miflora_sensor.sunlight(), 'temperature': miflora_sensor.read_temperature(), 
            'batteryLevel': miflora_sensor.get_battery_level()}
        ],
        'temperatureGeneral': temp_sensor.read_temperature(),
        'humidityGeneral': temp_sensor.read_humidity()
    })


def temp():
    MifloraSensor.scan()


def job_state_listener(event):
    if event.exception:
        print('EXCEPTION: The job crashed')
    elif event.code == EVENT_JOB_EXECUTED:
        print('Job worked')
    elif event.code == EVENT_JOB_MISSED:
        print('Job missed')
    else:
        print('Unknown Event!')


if __name__ == '__main__':
    sched = BlockingScheduler()
    sched.add_job(query_sesnor_values, 'interval', seconds=5, id='query_sensor_values')  # noqa: E501
    # sched.add_job(printA, 'interval', seconds=10, id='printA')
    sched.add_listener(job_state_listener, EVENT_JOB_EXECUTED | EVENT_JOB_ERROR | EVENT_JOB_MISSED)  # noqa: E501
    sched.start()
    # temp()


# def pp():
#    f = open("demofile2.txt", "a")
#    f.write("Content :)")
#    f.close()
