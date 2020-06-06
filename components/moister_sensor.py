from grove.adc import ADC
import enum


class MoistureSensor:
    """ # noqa: E501
    [Analog] 
    Moisture Sensor class for:
        Moisture Sensor (https://wiki.seeedstudio.com/Grove-Moisture_Sensor/)
        Capacitive Moisture Sensor (https://wiki.seeedstudio.com/Grove-Capacitive_Moisture_Sensor-Corrosion-Resistant/)
    Args:
        channel(int): number of analog pin/channel the sensor connected.
        sensor_type(MoistureSensorType): enum of MoistureSensorType indicating its type
    """
    def __init__(self, channel, sensor_type):
        self.channel = channel
        self.sensor_type = sensor_type
        # Analog to Digital Converter (ADC) - external chip unit on grove pi hat  # noqa: E501
        self.adc = ADC()

    @property
    def sensor_type(self):
        """Get moisture sensor type - either STANDARD (1) or CAPACITIVE (2)"""
        return self.sensor_type

    def readMoisture(self):
        """
        Get the moisture strength value/voltage

        Moisture Sensor:
        Min  Max  Condition
        0    0    open air
        0    300  dry soil
        300  700  humid soil
        700  950  water

        Capacitive Moisture Sensor: todo!!!!
        Min  Max  Condition
        0    0    open air
        0    300  dry soil
        300  700  humid soil
        700  950  water

        Returns:
            (int): voltage, in mV [millivolt = 0.001 V]
        """
        value = self.adc.read_voltage(self.channel)
        return value


class MoistureSensorType(enum.Enum):
    STANDARD = '1'
    CAPACITIVE = '2'
