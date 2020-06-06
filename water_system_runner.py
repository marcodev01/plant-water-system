import sched
import time

from components import Relay
from components import TemperatureHumiditySensor, TempHumSensorType
from components import MoistureSensor, MoistureSensorType

relay = Relay(pin=5)
temp_sensor = TemperatureHumiditySensor(channel=16, sensor_type=TempHumSensorType.PRO.value)  # noqa: E501
moister_standard = MoistureSensor(channel=0, sensor_type=MoistureSensorType.STANDARD)  # noqa: E501
moister_capacitive = MoistureSensor(channel=2, sensor_type=MoistureSensorType.CAPACITIVE)  # noqa: E501
