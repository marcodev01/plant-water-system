import time
from src.waterSystem.components import Relay
from src.waterSystem.components import TemperatureHumiditySensor, TempHumSensorType
from src.waterSystem.components import MoistureSensor, MoistureSensorType
from src.waterSystem.components import MifloraSensor
from src.waterSystem.components import SunlightSensor
from src.waterSystem.components import UltrasonicRanger


relay = Relay(pin=5)
relay_channel_1 = Relay(pin=22)
relay_channel_2 = Relay(pin=23)

temparature_humidity_sensor = TemperatureHumiditySensor(channel=16, sensor_type=TempHumSensorType.PRO.value)
moisture_capacitive_sensor_1 = MoistureSensor(channel=2, sensor_type=MoistureSensorType.CAPACITIVE.value)
moisture_capacitive_sensor_2 = MoistureSensor(channel=0, sensor_type=MoistureSensorType.CAPACITIVE.value)
sunlight_sensor = SunlightSensor()
ultra_sonic_ranger = UltrasonicRanger(pin=18)


def run_standard_relay():
    try:
        while True:
            relay.on()
            time.sleep(4)
            relay.off()
            time.sleep(2)
    except:
        # assure relay is switched off with ctrl+c
        relay.off()
        

def run_two_channel_relay():
    try:
        while True:
            relay_channel_1.on()
            time.sleep(2)
            relay_channel_1.off()
            relay_channel_2.on()
            time.sleep(2)
            relay_channel_2.off()
    except:
        # assure channel relays are switched off with ctrl+c
        relay_channel_1.off()
        relay_channel_2.off()


def run_temp_hum_pro_sensor():
    while True:
        print("Temperature °C: ", temparature_humidity_sensor.read_temperature())
        print("Humidity %: ", temparature_humidity_sensor.read_humidity())
        time.sleep(3)


def run_moisture_capacitive_sensor_1():
    while True:
        print("Moisture type: ", moisture_capacitive_sensor_1.sensor_type)
        print("Moisture value %: ", moisture_capacitive_sensor_1.read_moisture())
        time.sleep(1)


def run_moisture_capacitive_sensor_2():
    while True:
        print("Moisture type: ", moisture_capacitive_sensor_2.sensor_type)
        print("Moisture value %: ", moisture_capacitive_sensor_2.read_moisture())
        time.sleep(1)


def run_miflora_sensor():
    while True:
        miflora_sensor = MifloraSensor("80:EA:CA:89:60:A7")
        print("Miflora mositure %: ", miflora_sensor.read_moisture())
        print("Miflora sunlight (lux): ", miflora_sensor.read_sunlight())
        print("Miflora conductivity (µS/cm): ", miflora_sensor.read_conductivity())
        print("Miflora temperature °C: ", miflora_sensor.read_temperature())
        print("Miflora battery %: ", miflora_sensor.get_battery_level())
        time.sleep(5)


def run_sunlight_sensor():
    while True:
        print(f'Visible (lumen): {sunlight_sensor.readVisible()} UV (index): {sunlight_sensor.readUV()} IR: {sunlight_sensor.readIR()}', end=' ')
        print('\r', end='')
        time.sleep(1)

def run_ultra_sonic_ranger():
    while True:
        print(f'Distance: {ultra_sonic_ranger.get_distance()} cm')
        # print(f'Converted distance: {ultra_sonic_ranger.convert_distance_to_water_level()} %')
        time.sleep(1)



#############################
# run sensor by comment out #
# exit by ctrl + c          #
#############################

# run_standard_relay()
# run_two_channel_relay()

# run_temp_hum_pro_sensor()

# run_moisture_capacitive_sensor_1()
# run_moisture_capacitive_sensor_2()

# run_miflora_sensor()

# run_sunlight_sensor()

run_ultra_sonic_ranger()
