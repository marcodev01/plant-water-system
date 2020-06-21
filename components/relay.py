#!/usr/bin/env python3

from grove.gpio import GPIO


class Relay(GPIO):
    """
    [Digital GPIO]
    Relay class for:
        Relay (https://wiki.seeedstudio.com/Grove-Relay/)
    2-Channel Relay:
        2-Channel SPDT Relay (https://wiki.seeedstudio.com/Grove-2-Channel_SPDT_Relay/)

    -- A relay is an electrically operated switch --
    Note: 2-Channel SPDT Relay runs only on 5v

    GPIO mode is set on BCM

    Args:
        pin1(int): number of GPIO pin the relay switch 1 is connected
        pin2(int): number of GPIO pin the relay switch 2 is connected
    """
    def __init__(self, pin):
        super(Relay, self).__init__(pin, GPIO.OUT)

    def on(self):
        """ switch on electric circuit channel 1"""
        self.write(1)

    def off(self):
        """" switch off electric circuit channel 1"""
        self.write(0)
