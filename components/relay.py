#!/usr/bin/env python3

from grove.gpio import GPIO


class Relay(GPIO):
    """
    [Digital]
    Relay class for:
        Relay (https://wiki.seeedstudio.com/Grove-Relay/)
        2-Channel SPDT Relay (https://wiki.seeedstudio.com/Grove-2-Channel_SPDT_Relay/)

    -- A relay is an electrically operated switch --

    Args:
        pin(int): number of digital pin the relay connected
    """
    def __init__(self, pin):
        super(Relay, self).__init__(pin, GPIO.OUT)

    def on(self):
        """ switch on electric circuit """
        self.write(1)

    def off(self):
        """ switch off electric circuit """
        self.write(0)
