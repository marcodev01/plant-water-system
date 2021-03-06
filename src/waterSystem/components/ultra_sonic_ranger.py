#!/usr/bin/env python3

import time
from grove.gpio import GPIO
 
usleep = lambda x: time.sleep(x / 1000000.0)
 
_TIMEOUT1 = 1000
_TIMEOUT2 = 10000

_MAX_WATER_LEVEL_CM = 1.5
_MIN_WATER_LEVEL_CM = 11
 
class UltrasonicRanger(object):
    """
    [Digital GPIO]
    Ultra Soonic Ranger class for:
        Ultra Sonic Ranger (https://wiki.seeedstudio.com/Grove-Ultrasonic_Ranger/)

    Args:
        pin(int): number of digital pin/channel the sensor connected.

    """
    def __init__(self, pin):
        self.dio =GPIO(pin)
 
    def get_distance(self):
        self.dio.dir(GPIO.OUT)
        self.dio.write(0)
        usleep(2)
        self.dio.write(1)
        usleep(10)
        self.dio.write(0)
 
        self.dio.dir(GPIO.IN)
 
        t0 = time.time()
        count = 0
        while count < _TIMEOUT1:
            if self.dio.read():
                break
            count += 1
        if count >= _TIMEOUT1:
            return None
 
        t1 = time.time()
        count = 0
        while count < _TIMEOUT2:
            if not self.dio.read():
                break
            count += 1
        if count >= _TIMEOUT2:
            return None
 
        t2 = time.time()
 
        dt = int((t1 - t0) * 1000000)
        if dt > 530:
            return None
 
        distance = ((t2 - t1) * 1000000 / 29 / 2) # cm
 
        return round(distance, 1)

    def convert_distance_to_water_level(self):
        distance = self.get_distance()
        
        if distance is None:
            return -1

        absolute_distance_cm = self.get_distance() - _MIN_WATER_LEVEL_CM
        distance_percentage = (absolute_distance_cm * 100) / _MAX_WATER_LEVEL_CM
        water_level_percentage =  100 - distance_percentage
        return round(water_level_percentage, 1)


        
 
