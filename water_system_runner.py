#!/usr/bin/env python3

from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.events import EVENT_JOB_ERROR, EVENT_JOB_EXECUTED, EVENT_JOB_MISSED  # noqa: E501
from components import Relay
from components import TemperatureHumiditySensor, TempHumSensorType
from components import MoistureSensor, MoistureSensorType
from components import MifloraSensor

relay = Relay(pin=5)
temp_sensor = TemperatureHumiditySensor(channel=16, sensor_type=TempHumSensorType.PRO.value)  # noqa: E501
moister_standard = MoistureSensor(channel=0, sensor_type=MoistureSensorType.STANDARD.value)  # noqa: E501
moister_capacitive = MoistureSensor(channel=2, sensor_type=MoistureSensorType.CAPACITIVE.value)  # noqa: E501
miflora_sensor = MifloraSensor("80:EA:CA:89:60:A7")

def query_moisture(sensor):
    moisture = sensor.read_moisture()
    
    print('Moisture: ', moisture)  # todo: save to file


def query_temperature(sensor):
    temperature = sensor.read_temperature()
    print('Temperature: ', temperature)  # todo: save to file


def query_humidity(sensor):
    humidity = sensor.read_humidity()
    print('Humidity: ', humidity)  # todo: save to file


def query_sesnor_values():
    query_moisture(moister_standard)
    query_moisture(moister_capacitive)
    query_temperature(temp_sensor)
    query_humidity(temp_sensor)
    
    vall = miflora_sensor.get_battery_level()
    print('read_sunlight: ', vall)
    
    
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
