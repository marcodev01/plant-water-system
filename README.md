# Chilli Plant Water System

The "chilli" plant water system is controlled by an Raspbery PI 3 with the [Grove Base Hat](https://wiki.seeedstudio.com/Grove_Base_Hat_for_Raspberry_Pi/) 
and several connected sensors of Grove's ecosystem as well as Xiaomi Mi Flora Plant Sensor. The irrigation is electrically opererated by 5V water pumps which are controlled by 3.3V and 5V relays.
Application Architecture:

* Water System Runner
* Plant Water System API
* Plant Water Admin APP (Progressive Web App) **TODO**

## Water System Runner
The water system runner is a simple Python 3.7 application running two parallel jobs scheduled with the Python library [Advanced Python Scheduler](https://apscheduler.readthedocs.io/en/stable/).

The first job is reading and persisting values from various sensors with a **time stamp** into a [tinyDB](https://tinydb.readthedocs.io/en/stable/) table named *sensor_history*. _Note: For certain sensor values it converts and round them to legbible units_. 

The second job is reading the most recent data entry (by time stamp) from table *sensor_history* and compares them with the defined threshold values. For plants that fall below this threshold value the water pump is started. The threshold values are defined in a table named *plants_configuration* among other configurations for sensor channels, relay pins and watering duration/iteration etc.

A third job is cleaning up the *sensor_history* database from old values. The max age of *sensor_history* values can be configured in a table named *jobs_configuration*. 

All actions, warnings and errors are [logged](https://docs.python.org/3/library/logging.html) in *water_system.log* 

## API
An interface for the Chilli Plant Water System REST-API is implemented with [FastAPI](https://fastapi.tiangolo.com/). 
It provides Endpoints to manage plant configurtions, read logs, start/pause the water system etc. See full API documentation: http://{API_URI}/docs.

The API is operated on a ASGI server by [uvicorn](https://www.uvicorn.org/)

All actions, api accesses and errors are [logged](https://docs.python.org/3/library/logging.html) in *api.log* 

### Libraries
 * Groove Py: https://github.com/Seeed-Studio/grove.py
 * temp & humidity sensor: https://github.com/Seeed-Studio/Seeed_Python_DHT
 * sunlight sensor: https://github.com/Seeed-Studio/Seeed_Python_SI114X
 * MiFlora: https://github.com/basnijholt/miflora
 * Advanced Python Scheduler: https://apscheduler.readthedocs.io/en/stable/
 * tinyDB: https://tinydb.readthedocs.io/en/stable/
 * logging: https://docs.python.org/3/library/logging.html
 * dateTime: https://docs.python.org/3/library/datetime.html
 * FastAPI: https://fastapi.tiangolo.com/

# Setup dev environment
Allow sibling packages in python with virtual environment: [stack overflow thread](https://stackoverflow.com/questions/6323860/sibling-package-imports/50193944#50193944)

Start API server in dev environment: ```uvicorn api:app --reload```
