import time
from components import Relay
from components import TemperatureHumiditySensor, TempHumSensorType
from components import MoistureSensor, MoistureSensorType


relay = Relay(pin=5)
temp = TemperatureHumiditySensor(channel=16, sensor_type=TempHumSensorType.PRO.value)  # noqa: E501
temp2 = TemperatureHumiditySensor(channel=5, sensor_type=TempHumSensorType.STANDARD.value)  # noqa: E501

moister = MoistureSensor(channel=2, sensor_type=MoistureSensorType.STANDARD)  # noqa: E501


def relay():
    while True:
        relay.on()
        time.sleep(2)
        relay.off()
        time.sleep(2)


def readTemp():
    while True:
        print("Temp: ", temp.readTemperature())
        print("Humidity: ", temp.readHumidity())
        print("dht_sensor_type: ", temp.dht_sensor_type)
        
        print("Temp2: ", temp2.readTemperature())
        print("Humidity2: ", temp2.readHumidity())
        print("dht_sensor_type2: ", temp2.dht_sensor_type)
        time.sleep(3)


def moister():
    while True:
        print("Moisture type: ", moister.sensor_type)
        print("Moisture val: ", moister.moisture)

readTemp()
