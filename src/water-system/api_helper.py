
from typing import Dict, Union
from tinydb import TinyDB
import logging


# log configurations
logging.basicConfig(filename='src/log/api.log',
                    filemode='a', format='%(asctime)s - %(levelname)s - %(message)s',
                    datefmt='%d-%m-%y %H:%M:%S', level=logging.INFO)
logger = logging.getLogger(__name__) # module logger instance

# history db initialisation
plant_db = TinyDB('src/db/plant_history.json')
sensor_history = plant_db.table('sensor_history')
# master data db initialisation
master_data_db = TinyDB('src/db/master_data.json')
plants_conf = master_data_db.table('plants_configuration')


###########################
# plant history db helper #
###########################
def get_plant_configurations() -> Dict[str, Union[str, int]]:
    return plants_conf.all()

