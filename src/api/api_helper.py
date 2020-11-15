
from typing import List, Union
from tinydb import TinyDB
import logging

from tinydb.table import Document


logger = logging.getLogger('api') # module logger instance


###########################
# plant history db helper #
###########################

def get_water_system_log_fragment(nmb_lines: int) -> str:
    water_sys_log_path = '../log/water_system.log'
    log_fragment = ''
    with open(water_sys_log_path) as file:
        for line in (file.readlines() [-nmb_lines:]): 
            log_fragment = log_fragment + line + '\n'
    return log_fragment

def get_api_log_fragment(nmb_lines: int) -> str:
    water_sys_log_path = '../log/api.log'
    log_fragment = ''
    with open(water_sys_log_path) as file:
        for line in (file.readlines() [-nmb_lines:]): 
            log_fragment = log_fragment + line + '\n'
    return log_fragment
