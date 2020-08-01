import time
from components import Relay
from components import TemperatureHumiditySensor, TempHumSensorType
from components import MoistureSensor, MoistureSensorType
from components import MifloraSensor


relay = Relay(pin=5)
channel1_relay = Relay(pin=22)
channel2_relay = Relay(pin=23)
temp = TemperatureHumiditySensor(channel=16, sensor_type=TempHumSensorType.PRO.value)
moister_stand = MoistureSensor(channel=0, sensor_type=MoistureSensorType.STANDARD)
moisture_cap = MoistureSensor(channel=2, sensor_type=MoistureSensorType.CAPACITIVE)
# miflora_sensor = MifloraSensor("80:EA:CA:89:60:A7")


def test_relay():
    while True:
        relay.on()
        time.sleep(2)
        relay.off()
        time.sleep(2)
        

def two_channel_relay():
    while True:
        channel1_relay.on()
        time.sleep(2)
        channel1_relay.off()
        channel2_relay.on()
        time.sleep(2)
        channel2_relay.off()
        
def off_channel_relay():
    channel1_relay.off()
    channel2_relay.off()


def read_temp():
    while True:
        print("Temp: ", temp.read_temperature())
        print("Humidity: ", temp.read_humidity())
        print("dht_sensor_type: ", temp.dht_sensor_type)
        time.sleep(3)


def read_moisture_stand():
    while True:
        print("Moisture type: ", moister_stand.sensor_type)
        print("Moisture val: ", moister_stand.read_moisture())
        print("Moisture type: ", moisture_cap.sensor_type)
        print("Moisture val: ", moisture_cap.read_moisture())
        time.sleep(1)


def read_moisture_cap():
    while True:
        print("Moisture type: ", moisture_cap.sensor_type)
        print("Moisture val: ", moisture_cap.read_moisture())
        time.sleep(0.5)

def read_miflora():
    while True:
        miflora_sensor = MifloraSensor("80:EA:CA:89:60:A7")
        print("Miflora mositure: ", miflora_sensor.read_moisture())
        print("Miflora sunlight: ", miflora_sensor.read_sunlight())
        print("Miflora conductivity: ", miflora_sensor.read_conductivity())
        print("Miflora temperature: ", miflora_sensor.read_temperature())
        time.sleep(3)


test_relay()
# two_channel_relay()
# off_channel_relay()
# read_moisture_stand()
# read_moisture_cap()
# read_miflora()