#!/usr/bin/env python3

from enum import IntEnum

class WaterSystemState(IntEnum):
    """ see docs: https://apscheduler.readthedocs.io/en/stable/modules/schedulers/base.html """
    STATE_STOPPED = 0
    STATE_RUNNING = 1
    STATE_PAUSED = 2