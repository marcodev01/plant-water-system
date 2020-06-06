from apscheduler.schedulers.background import BackgroundScheduler
from components import Relay
from components import TemperatureHumiditySensor, TempHumSensorType
from components import MoistureSensor, MoistureSensorType

# relay = Relay(pin=5)
# temp_sensor = TemperatureHumiditySensor(channel=16, sensor_type=TempHumSensorType.PRO.value)  # noqa: E501
# moister_standard = MoistureSensor(channel=0, sensor_type=MoistureSensorType.STANDARD)  # noqa: E501
# moister_capacitive = MoistureSensor(channel=2, sensor_type=MoistureSensorType.CAPACITIVE)  # noqa: E501

def pp():
    f = open("test.txt", "a")
    f.write("Hello1oooo")
    f.close()

def my_listener(event):
    if event.exception:
        print('The job crashed :(')
    else:
        print('The job worked :)')



sched = BackgroundScheduler(daemon=True)
sched.add_job(lambda: pp,'interval',seconds=1)
sched.add_listener(my_listener, EVENT_JOB_EXECUTED | EVENT_JOB_ERROR)
sched.start()


