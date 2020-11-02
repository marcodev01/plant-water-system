#!/usr/bin/env python3

import argparse
import re

from miflora.miflora_poller import MiFloraPoller, MI_CONDUCTIVITY, MI_MOISTURE, MI_LIGHT, MI_TEMPERATURE, MI_BATTERY
from btlewrap.bluepy import BluepyBackend
from miflora import miflora_scanner


class MifloraSensor:
    """
    [Bluetooth]
    Miflora Sensor class for:
        Miflora (https://www.home-assistant.io/integrations/miflora/)
        Library for Miflora (https://github.com/open-homeautomation/miflora)

    Args:
        adress(string): MAC address of Miflora Sensor
    """
    def __init__(self, address):
        if self.__valid_mac_address(address):
            self.poller = MiFloraPoller(address, BluepyBackend)

    def __valid_mac_address(self, mac, pat=re.compile(r"[0-9A-F]{2}:[0-9A-F]{2}:[0-9A-F]{2}:[0-9A-F]{2}:[0-9A-F]{2}:[0-9A-F]{2}")):
        # Check for valid mac adresses
        if not pat.match(mac.upper()):
            raise argparse.ArgumentTypeError('The MAC address "{}" seems to be in the wrong format'.format(mac))
        return True

    def get_history(self):
        return self.poller.fetch_history()

    def clear_history(self):
        self.poller.clear_history()

    def get_firmware_version(self):
        return self.poller.firmware_version()

    def get_name(self):
        return self.poller.name()

    def get_battery_level(self):
        """in %"""
        return self.poller.parameter_value(MI_BATTERY)

    def read_temperature(self):
        """Read temperature in degrees [Celsuis]"""
        return self.poller.parameter_value(MI_TEMPERATURE)

    def read_moisture(self):
        """Read moisture in %"""
        return self.poller.parameter_value(MI_MOISTURE)

    def read_sunlight(self):
        """Read light intesity in lux"""
        return self.poller.parameter_value(MI_LIGHT)

    def read_conductivity(self):
        """in Mikrosiemens (µS/cm) - Fertility (Fruchtbarkeit) / Bodenleitfähigkeit"""
        return self.poller.parameter_value(MI_CONDUCTIVITY)

    @staticmethod
    def scan():
        print('Scanning for 10 seconds...')
        devices = miflora_scanner.scan(BluepyBackend, 10)
        print('Found {} devices:'.format(len(devices)))
        for device in devices:
            print('  {}'.format(device))
