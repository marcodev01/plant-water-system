import seeed_dht
import enum

class TemperatureHumiditySensor:
    """
    Temperature and Humidity Sensor class for:
        Temperature&Humidity Sensor Pro [DHT22] (https://wiki.seeedstudio.com/Grove-Temperature_and_Humidity_Sensor_Pro/)
        Temperature&Humidity Sensor [DHT11] (https://wiki.seeedstudio.com/Grove-TemperatureAndHumidity_Sensor/)

    Args:
        channel(int): number of analog pin/channel the sensor connected.
        sensor_type(MoistureSensorType): enum of MoistureSensorType indicating its type [DHT11 is type '11', DHT22 is type '22']
    """
    def __init__(self, channel, sensor_type):
        self.dht_sensor = seeed_dht.DHT(sensor_type, channel)

    @property
    def temperature(self):
        """Read temperature in degrees [Celsuis]"""
        temp = self.dht_sensor.read()[1]
        return temp 

    @property
    def humidity(self):
        """Read humidity in %"""
        humi = self.dht_sensor.read()[0]
        return humi

    @property
    def dht_sensor_type(self):
        return self.dht_sensor.dht_type


class TempHumSensorType(enum.Enum):
    PRO = 22
    STANDARD = 11