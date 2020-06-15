#!/usr/bin/env python3

from grove.adc import ADC
import enum


class MoistureSensor:
    """
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
        self.sen_type = sensor_type
        # Analog to Digital Converter (ADC) - external chip unit on grove pi hat
        self.adc = ADC()

    @property
    def sensor_type(self):
        """Get moisture sensor type - either STANDARD (1) or CAPACITIVE (2)"""
        return self.sen_type

    def read_moisture(self):
        """
        Get the moisture strength value/voltage

        voltage, in mV [millivolt = 0.001 V]
        Moisture Sensor - Min: 0   Max: 1500
        Capacitive Moisture Sensor - Min: 2000   Max: 1450 / 1250 (Water)

        Returns:
            (int): mosture in %
        """

        min_moisture = 1000 if self.sen_type == MoistureSensorType.STANDARD else 2020
        max_moisture = 1800 if self.sen_type == MoistureSensorType.STANDARD else 1480
        

        value = self.adc.read_voltage(self.channel)
        print('RAW VALUE: ', value)

        return self.__convert_moisture_voltage_to_percent(min_moisture, max_moisture, value)


    def __convert_moisture_voltage_to_percent(self, min_val, max_val, val):
        max_absolute =  max_val if min_val < max_val else abs(max_val - min_val)
        val_absolute =  val - min_val if min_val < max_val else min_val - val
        
        return round((val_absolute / max_absolute) * 100)


class MoistureSensorType(enum.Enum):
    STANDARD = '1'
    CAPACITIVE = '2'
