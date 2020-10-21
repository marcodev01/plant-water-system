#!/usr/bin/env python3

import seeed_si114x

class SunlightSensor:
    """
    [I2C]
    Sunlight Sensor class for:
        Moisture Sensor (https://wiki.seeedstudio.com/Grove-Moisture_Sensor/)
    """
    def __init__(self):
        self.SI1145 = seeed_si114x.grove_si114x()

    def readVisible(self):
        """ visible light of Ambient in lumen """
        return self.SI1145.ReadVisible

    def readUV(self):
        """ ultraviolet index (see doc for value meaning)"""
        return self.SI1145.ReadUV/100
    
    def readIR(self):
        """ infrared light of Ambient"""
        return self.SI1145.ReadIR 