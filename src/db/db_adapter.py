#!/usr/bin/env python3
from tinydb import TinyDB

SENSOR_HISTORY_TABLE_NAME = 'sensor_history'
PLANTS_CONFIGURATION_TABLE_NAME = 'plants_configuration'
SCHEDULED_JOBS_CONFIGURATION_TABLE_NAME = 'jobs_configuration'

class DbAdapter(object):
    """ Database adapter to create a singelton TinyDB instance / connection """
    _instance = None
    _plant_db_path = '../db/plant_history.json'
    _master_data_db_path = '../db/master_data.json'

    def __new__(cls, *args, **kwargs):
        if not isinstance(cls._instance, cls):
            cls._instance = object.__new__(cls, *args, **kwargs)
            cls.plant_db = TinyDB(DbAdapter._plant_db_path)
            cls.master_data_db = TinyDB(DbAdapter._master_data_db_path)
        return cls._instance

