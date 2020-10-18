# Chilli plant water system

The chilli water plant system is controlled by an Raspbery PI 3 with the [Grove Base Hat](https://wiki.seeedstudio.com/Grove_Base_Hat_for_Raspberry_Pi/) 
and several connected sensors of Grove's ecosystem as well as Xiaomi Mi Flora Plant Sensor. The water system itself is electrically opererated by 5V water pumps and controlled with relays.
The system is consiting of following applications:

* Water system runner - *written in phyton 3.x*
* TODO: App

## Water System Runner
The water system runner is a simple Python application which reads values from various sensors - for certain sensor values it converts and round them to legbible units.
Finally, the values are persited with a **time stamp** into a [tinyDB](https://tinydb.readthedocs.io/en/stable/) table named *sensor_history*.

In a second step the most recent values were read from *sensor_history* and checked with the limit settings specified in *master_db*. 
In addition the sensor channels, relay pins and watering duration/iteration is configured in *master_db* database.

The executions for reading and persisting the sensor values as well as checks for watering are scheduled with the Python library [Advanced Python Scheduler](https://apscheduler.readthedocs.io/en/stable/)

All actions, warnings and errors are [logged](https://docs.python.org/3/library/logging.html) in *water_system.log* 

### Libraries
 * Groove Py: https://github.com/Seeed-Studio/grove.py
 * temp & humidity sensor: https://github.com/Seeed-Studio/Seeed_Python_DHT
 * MiFlora: https://github.com/basnijholt/miflora
 * Advanced Python Scheduler: https://apscheduler.readthedocs.io/en/stable/
 * tinyDB: https://tinydb.readthedocs.io/en/stable/
 * logging: https://docs.python.org/3/library/logging.html
 * dateTime: https://docs.python.org/3/library/datetime.html

# TODO
* implement Sunlight sensor: https://github.com/Seeed-Studio/Seeed_Python_SI114X / https://wiki.seeedstudio.com/Grove-Sunlight_Sensor/
* Configuration App

##### Author: Marc Touw
