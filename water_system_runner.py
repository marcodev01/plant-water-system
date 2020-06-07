from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.events import EVENT_JOB_ERROR, EVENT_JOB_EXECUTED, EVENT_JOB_MISSED
import time
# from components import Relay
# from components import TemperatureHumiditySensor, TempHumSensorType
# from components import MoistureSensor, MoistureSensorType

# relay = Relay(pin=5)
# temp_sensor = TemperatureHumiditySensor(channel=16, sensor_type=TempHumSensorType.PRO.value)  # noqa: E501
# moister_standard = MoistureSensor(channel=0, sensor_type=MoistureSensorType.STANDARD)  # noqa: E501
# moister_capacitive = MoistureSensor(channel=2, sensor_type=MoistureSensorType.CAPACITIVE)  # noqa: E501

def pp():
    f = open("demofile2.txt", "a")
    f.write("Content :)")
    f.close()

def my_listener(event):
    print(event)
    if event.exception:
        print('The job crashed :(')
    elif event.code == EVENT_JOB_EXECUTED:
        print('!!!The job worked :)')
    else:
        print('The job worked :)')

def printA():
    print("HEllou :)")

def loop():
    while True:
        print('Im Looping')
        time.sleep(5)



if __name__ == '__main__':
    sched = BlockingScheduler()
    sched.add_job(pp,'interval',seconds=1, id='pp')
    sched.add_job(printA, 'interval', seconds=10, id='printA')
    sched.add_listener(my_listener, EVENT_JOB_EXECUTED | EVENT_JOB_ERROR | EVENT_JOB_MISSED) 
    sched.start()


