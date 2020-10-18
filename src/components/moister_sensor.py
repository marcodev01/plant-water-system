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
        self.channel = channel # TODO: evtl. remove redundant variable
        self.sen_type = sensor_type # TODO: evtl. remove redundant variable
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
        Moisture Sensor - Min: 0   Max: 1800
        Capacitive Moisture Sensor - Min: 2020   Max: 1300

        Returns:
            (int): mosture in %
        """

        min_moisture = 0 if self.sen_type == MoistureSensorType.STANDARD.value else 2020
        max_moisture = 1800 if self.sen_type == MoistureSensorType.STANDARD.value else 1300
        

        value = self.adc.read_voltage(self.channel)

        return self.__convert_moisture_voltage_to_percent(min_moisture, max_moisture, value)


    def __convert_moisture_voltage_to_percent(self, min_val, max_val, val):
        max_absolute =  max_val if min_val < max_val else abs(max_val - min_val)
        val_absolute =  val - min_val if min_val < max_val else min_val - val
        
        result = round((val_absolute / max_absolute) * 100)
        
        # compensate tolerances
        if result < 0:
            result = 0
        elif result > 100:
            result = 100
        
        return result


class MoistureSensorType(enum.Enum):
    STANDARD = 'moisture_standard'
    CAPACITIVE = 'moisture_capacitve'
